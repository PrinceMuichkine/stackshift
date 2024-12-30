import path from 'path';
import fs from 'fs-extra';
import { CodebaseAnalysis } from '../types';

export async function transformViteConfig(
  projectPath: string, 
  analysis: CodebaseAnalysis, 
  dryRun: boolean
): Promise<void> {
  const nextConfig = generateNextConfig(analysis.configuration);
  const configPath = path.join(projectPath, 'next.config.js');

  if (dryRun) {
    console.log('Would create next.config.js:');
    console.log(nextConfig);
    return;
  }

  await fs.writeFile(configPath, nextConfig);
}

function generateNextConfig(config: CodebaseAnalysis['configuration']): string {
  const { aliases, environment } = config.viteConfig;

  return `/** @type {import('next').NextConfig} */
const nextConfig = {
  webpack: (config) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      ${Object.entries(aliases)
        .map(([key, value]) => `'${key}': '${value}'`)
        .join(',\n      ')}
    };
    return config;
  },
  env: {
    ${Object.entries(environment)
      .map(([key, value]) => `'${key}': '${value}'`)
      .join(',\n    ')}
  },
  // Additional Next.js config from analysis
  ${config.suggestedNextConfig}
};

module.exports = nextConfig;
`;
} 