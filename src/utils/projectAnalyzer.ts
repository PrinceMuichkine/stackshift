import fs from 'fs-extra';
import path from 'path';
import { ProjectAnalysis, Dependency, AIAnalysis, ProjectAnalyzerOptions } from '../types';
import { AIAnalyzer } from './aiAnalyzer';

export class ProjectAnalyzer {
  private projectPath: string;
  private aiAnalyzer: AIAnalyzer;

  constructor(projectPath: string) {
    this.projectPath = projectPath;
    this.aiAnalyzer = new AIAnalyzer(projectPath);
  }

  async analyzeProject(options: ProjectAnalyzerOptions = {}): Promise<ProjectAnalysis> {
    if (!(await this.isValidProject())) {
      throw new Error('Invalid project directory. Make sure package.json exists.');
    }

    console.log('Starting basic project analysis...');
    const basicAnalysis = await this.performBasicAnalysis(options.config);
    console.log('Basic project analysis complete');
    
    let aiAnalysis: AIAnalysis | undefined;
    if (!options.skipAI) {
      try {
        console.log('Starting AI-assisted analysis...');
        aiAnalysis = await this.aiAnalyzer.analyzeCodebase(options.nonInteractive);
        console.log('AI-assisted analysis complete');
      } catch (error) {
        console.error('Error during AI analysis:', error);
        console.log('Continuing with basic analysis results');
      }
    }

    console.log('Combining analysis results...');
    const finalAnalysis = {
      ...basicAnalysis,
      aiSuggestions: aiAnalysis,
      routingStructure: aiAnalysis?.routing.suggestedNextjsStructure ?? []
    };
    console.log('Project analysis complete');

    return finalAnalysis;
  }

  private async performBasicAnalysis(customConfigFiles?: string[]) {
    const packageJson = await this.readPackageJson();
    const requirementsTxt = await this.readRequirementsTxt();
    const pyprojectToml = await this.readPyprojectToml();
    
    const dependencies = await this.analyzeDependencies(packageJson, requirementsTxt, pyprojectToml);
    
    const tsConfig = await this.findTsConfig();
    const pythonConfig = await this.findPythonConfig();
    const testConfig = await this.findTestConfig();
    const lintConfig = await this.findLintConfig();
    const prettierConfig = await this.findPrettierConfig();
    const ciConfig = await this.findCiConfig();
    const containerizationConfig = await this.findContainerizationConfig();
    const configFiles = await this.findConfigFiles(customConfigFiles);

    return {
      framework: this.detectFramework(packageJson, pyprojectToml),
      dependencies,
      tsConfig,
      pythonConfig,
      testConfig,
      lintConfig, 
      prettierConfig,
      ciConfig,
      containerizationConfig,
      configFiles,
    };
  }

  private async isValidProject(): Promise<boolean> {
    return await fs.pathExists(path.join(this.projectPath, 'package.json'));
  }

  private async readPackageJson(): Promise<any> {
    const packageJsonPath = path.join(this.projectPath, 'package.json');
    return await fs.readJson(packageJsonPath);
  }

  private async readRequirementsTxt(): Promise<string | null> {
    const requirementsTxtPath = path.join(this.projectPath, 'requirements.txt');
    if (await fs.pathExists(requirementsTxtPath)) {
      return fs.readFile(requirementsTxtPath, 'utf-8');
    }
    return null;
  }

  private async readPyprojectToml(): Promise<any | null> {
    const pyprojectTomlPath = path.join(this.projectPath, 'pyproject.toml');
    if (await fs.pathExists(pyprojectTomlPath)) {
      return this.parseTOML(await fs.readFile(pyprojectTomlPath, 'utf-8'));
    }
    return null;
  }

  private async analyzeDependencies(packageJson: any, requirementsTxt: string | null, pyprojectToml: any | null): Promise<Dependency[]> {
    let dependencies: Dependency[] = [];

    if (packageJson) {
      const allDependencies = {
        ...packageJson.dependencies,
        ...packageJson.devDependencies
      };

      dependencies = dependencies.concat(
        Object.entries(allDependencies).map(([name, version]) => ({
          name,
          version: version as string,
          isCompatible: this.checkCompatibility(name),
          alternativePackage: this.suggestAlternative(name)
        }))
      );
    }

    if (requirementsTxt) {
      dependencies = dependencies.concat(
        requirementsTxt
          .split('\n')
          .map(line => line.trim())
          .filter(line => line && !line.startsWith('#'))
          .map(line => {
            const [name, version] = line.split('==');
            return {
              name,
              version,
              isCompatible: this.checkCompatibility(name),
              alternativePackage: this.suggestAlternative(name)
            };
          })
      );
    }

    if (pyprojectToml?.tool?.poetry?.dependencies) {
      dependencies = dependencies.concat(
        Object.entries(pyprojectToml.tool.poetry.dependencies).map(([name, version]) => ({
          name,
          version: version as string,
          isCompatible: this.checkCompatibility(name),
          alternativePackage: this.suggestAlternative(name)
        }))
      );
    }

    return dependencies;
  }

  private checkCompatibility(packageName: string): boolean {
    const incompatiblePackages = [
      'vite',
      '@vitejs/plugin-react',
      '@vitejs/plugin-vue'
    ];
    return !incompatiblePackages.includes(packageName);
  }

  private suggestAlternative(packageName: string): string | undefined {
    const alternatives: Record<string, string> = {
      'vite': 'next',
      '@vitejs/plugin-react': '@next/react',
      'react-router-dom': 'next/router'
    };
    return alternatives[packageName];
  }

  private async findTsConfig(): Promise<string | null> {
    const tsconfigPath = path.join(this.projectPath, 'tsconfig.json');
    if (await fs.pathExists(tsconfigPath)) {
      return tsconfigPath;
    }
    return null;
  }

  private async findPythonConfig(): Promise<string | null> {
    const pyprojectTomlPath = path.join(this.projectPath, 'pyproject.toml');
    if (await fs.pathExists(pyprojectTomlPath)) {
      return pyprojectTomlPath;
    }
    return null;
  }

  private async findTestConfig(): Promise<string | null> {
    const jestConfigPath = path.join(this.projectPath, 'jest.config.js');
    if (await fs.pathExists(jestConfigPath)) {
      return jestConfigPath;
    }

    const pytestIniPath = path.join(this.projectPath, 'pytest.ini');
    if (await fs.pathExists(pytestIniPath)) {
      return pytestIniPath;
    }

    return null;
  }

  private async findLintConfig(): Promise<string | null> {
    const eslintrcPath = path.join(this.projectPath, '.eslintrc');
    if (await fs.pathExists(eslintrcPath)) {
      return eslintrcPath;
    }
    return null;
  }

  private async findPrettierConfig(): Promise<string | null> {
    const prettierrcPath = path.join(this.projectPath, '.prettierrc');
    if (await fs.pathExists(prettierrcPath)) {
      return prettierrcPath;
    }
    return null;
  }

  private async findCiConfig(): Promise<string | null> {
    const githubCiPath = path.join(this.projectPath, '.github', 'workflows');
    if (await fs.pathExists(githubCiPath)) {
      return githubCiPath;
    }

    const gitlabCiPath = path.join(this.projectPath, '.gitlab-ci.yml');
    if (await fs.pathExists(gitlabCiPath)) {
      return gitlabCiPath;
    }

    return null;
  }

  private async findContainerizationConfig(): Promise<string | null> {
    const dockerfilePath = path.join(this.projectPath, 'Dockerfile');
    if (await fs.pathExists(dockerfilePath)) {
      return dockerfilePath;
    }
    return null;
  }

  private parseTOML(content: string): any {
    // Implement TOML parsing logic here
    // ...
  }

  private detectFramework(packageJson: any, pyprojectToml: any): string {
    // Check for Vite in dependencies or devDependencies
    const hasViteInDeps = packageJson?.dependencies?.vite || packageJson?.devDependencies?.vite;
    const hasVitePluginReact = packageJson?.dependencies?.['@vitejs/plugin-react'] || 
                              packageJson?.devDependencies?.['@vitejs/plugin-react'];
    
    if (hasViteInDeps || hasVitePluginReact) {
      return 'vite';
    }

    // Check for Vite in Python project
    if (pyprojectToml?.tool?.poetry?.dependencies?.vite) {
      return 'vite';
    }

    return 'unknown';
  }

  private async findConfigFiles(customConfigFiles?: string[]): Promise<string[]> {
    const configPatterns = [
      'vite.config.ts',
      'vite.config.js', 
      'tsconfig.json',
      '.env',
      '.env.*',
      ...(customConfigFiles || [])
    ];

    const configFiles: string[] = [];
    
    for (const pattern of configPatterns) {
      const files = await fs.pathExists(path.join(this.projectPath, pattern));
      if (files) {
        configFiles.push(pattern);
      }
    }

    return configFiles;
  }
} 