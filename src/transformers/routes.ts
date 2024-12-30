import path from 'path';
import fs from 'fs-extra';
import { CodebaseAnalysis, RouteInfo } from '../types';

export async function transformRoutes(
  projectPath: string,
  analysis: CodebaseAnalysis,
  dryRun: boolean
): Promise<void> {
  const { routes } = analysis.routing;
  
  // Create app directory
  const appDir = path.join(projectPath, 'src/app');
  if (!dryRun) {
    await fs.ensureDir(appDir);
  }

  // Transform each route
  for (const route of routes) {
    await transformRoute(projectPath, route, dryRun);
  }

  // Create root layout
  await createRootLayout(appDir, dryRun);
}

async function transformRoute(projectPath: string, route: RouteInfo, dryRun: boolean): Promise<void> {
  const { path: routePath, component } = route;
  const segments = routePath.split('/').filter(Boolean);
  
  // Convert route parameters to Next.js format
  const nextPath = segments
    .map(segment => segment.startsWith(':') ? `[${segment.slice(1)}]` : segment)
    .join('/');

  const pagePath = path.join(projectPath, 'src/app', nextPath, 'page.tsx');
  
  if (dryRun) {
    console.log(`Would create page: ${pagePath}`);
    return;
  }

  // Read original component
  const componentPath = await findComponentFile(projectPath, component);
  if (!componentPath) {
    console.warn(`Could not find component file for ${component}`);
    return;
  }

  const componentContent = await fs.readFile(componentPath, 'utf-8');
  const migratedContent = await migrateDataFetching(projectPath, componentContent, route);
  const nextContent = transformComponentToNextjs(migratedContent, route);

  await fs.ensureDir(path.dirname(pagePath));
  await fs.writeFile(pagePath, nextContent);
}

async function findComponentFile(projectPath: string, componentName: string): Promise<string | null> {
  const extensions = ['.tsx', '.jsx', '.ts', '.js'];
  const directories = ['src/components', 'src/pages', 'src'];

  for (const dir of directories) {
    for (const ext of extensions) {
      const filePath = path.join(projectPath, dir, `${componentName}${ext}`);
      if (await fs.pathExists(filePath)) {
        return filePath;
      }
    }
  }

  return null;
}

function transformComponentToNextjs(content: string, route: RouteInfo): string {
  // Basic transformation - you might want to make this more sophisticated
  return `import { Metadata } from 'next'
import { headers } from 'next/headers'

export const metadata: Metadata = {
  title: '${route.path}',
}

${route.hasLoaders ? `
export async function generateMetadata() {
  // TODO: Implement metadata generation
  return {}
}

export async function generateStaticParams() {
  // TODO: Implement static params if needed
  return []
}
` : ''}

export default function Page(${route.hasParams ? `{ params }: { params: { ${route.path.split('/').filter(s => s.startsWith(':')).map(s => `${s.slice(1)}: string`).join(', ')} } }` : ''}) {
  ${content.replace(/export\s+default\s+function\s+\w+\s*\([^)]*\)\s*{/, '').slice(0, -1)}
}`;
}

async function createRootLayout(appDir: string, dryRun: boolean): Promise<void> {
  const layoutContent = `
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'My Next.js App',
  description: 'Migrated from Vite',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}`;

  const layoutPath = path.join(appDir, 'layout.tsx');
  
  if (dryRun) {
    console.log('Would create root layout:', layoutPath);
    return;
  }

  await fs.writeFile(layoutPath, layoutContent);
}

// Handle more complex route patterns and parameters
function transformRouteParameters(routePath: string): string {
  const segments = routePath.split('/');
  const transformedSegments = segments.map(segment => {
    if (segment.startsWith(':')) {
      const paramName = segment.slice(1);
      return `[${paramName}]`;
    }
    if (segment.includes('(') && segment.includes(')')) {
      const [paramName, regex] = segment.slice(1, -1).split('(');
      return `[${paramName}:${regex}]`;
    }
    return segment;
  });
  return transformedSegments.join('/');
}

// Migrate route-specific data fetching logic
async function migrateDataFetching(projectPath: string, componentContent: string, route: RouteInfo): Promise<string> {
  // Check for data fetching patterns (e.g., useEffect, componentDidMount)
  const dataFetchingPatterns = [
    /useEffect\(\s*\(\s*\)\s*=>\s*{/,
    /componentDidMount\(\s*\)\s*{/,
  ];

  let migratedContent = componentContent;

  for (const pattern of dataFetchingPatterns) {
    if (pattern.test(componentContent)) {
      // Extract data fetching logic
      const dataFetchingCode = componentContent.match(pattern)?.[0];

      if (dataFetchingCode) {
        // Remove data fetching code from the component
        migratedContent = migratedContent.replace(dataFetchingCode, '');

        // Create a new API route file
        const apiRoutePath = path.join(projectPath, 'src/pages/api', `${route.path}.ts`);
        const apiRouteContent = `
          import { NextApiRequest, NextApiResponse } from 'next';

          export default async function handler(req: NextApiRequest, res: NextApiResponse) {
            // TODO: Implement data fetching logic here
            ${dataFetchingCode}

            res.status(200).json({ data: 'Placeholder data' });
          }
        `;

        await fs.ensureDir(path.dirname(apiRoutePath));
        await fs.writeFile(apiRoutePath, apiRouteContent);

        // Update the component to fetch data from the API route
        const dataFetchingReplacement = `
          const [data, setData] = useState(null);

          useEffect(() => {
            async function fetchData() {
              const res = await fetch('${route.path}');
              const json = await res.json();
              setData(json.data);
            }
            fetchData();
          }, []);
        `;

        migratedContent = migratedContent.replace(/export default function/, `${dataFetchingReplacement}\n\nexport default function`);
      }
    }
  }

  return migratedContent;
} 