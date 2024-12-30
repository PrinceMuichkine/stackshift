import path from 'path';
import fs from 'fs-extra';
import { CodebaseAnalysis } from '../types';

export async function transformPackageJson(
  projectPath: string,
  analysis: CodebaseAnalysis,
  dryRun: boolean
): Promise<void> {
  const packageJsonPath = path.join(projectPath, 'package.json');
  const packageJson = await fs.readJson(packageJsonPath);

  // Remove Vite dependencies
  analysis.dependencies.viteSpecific.forEach(dep => {
    delete packageJson.dependencies?.[dep];
    delete packageJson.devDependencies?.[dep];
  });

  // Add Next.js dependencies
  const nextDependencies = {
    'next': '^14.0.0',
    'react': '^18.2.0',
    'react-dom': '^18.2.0',
  };

  packageJson.dependencies = {
    ...packageJson.dependencies,
    ...nextDependencies
  };

  // Update scripts
  packageJson.scripts = {
    ...packageJson.scripts,
    dev: 'next dev',
    build: 'next build',
    start: 'next start',
    lint: 'next lint'
  };

  if (dryRun) {
    console.log('Would update package.json:', JSON.stringify(packageJson, null, 2));
    return;
  }

  await fs.writeJson(packageJsonPath, packageJson, { spaces: 2 });
} 