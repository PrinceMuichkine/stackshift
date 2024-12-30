import { AIAnalysis, CodebaseAnalysis, RoutingAnalysis, DependencyAnalysis, ConfigurationAnalysis, RouteInfo } from '../types';
import fs from 'fs-extra';
import path from 'path';
import { glob } from 'glob';
import { Anthropic } from '@anthropic-ai/sdk';

export class AIAnalyzer {
  private projectPath: string;
  private anthropic: Anthropic;

  constructor(projectPath: string) {
    this.projectPath = projectPath;
    this.anthropic = new Anthropic({
      apiKey: process.env.ANTHROPIC_API_KEY,
    });
  }

  async analyzeCodebase(nonInteractive: boolean = false): Promise<AIAnalysis> {
    try {
      console.log('Starting AI analysis...');
      
      // Check if directory exists first
      if (!await fs.pathExists(this.projectPath)) {
        const error = new Error(`ENOENT: no such file or directory '${this.projectPath}'`);
        error.name = 'ENOENT';
        throw error;
      }
      
      const relevantFiles = await this.getRelevantFiles();
      console.log(`Found ${relevantFiles.length} relevant files`);

      const codebaseContents = await this.readCodebaseFiles(relevantFiles);
      console.log('Read codebase files');

      console.log('Analyzing routing...');
      const routingAnalysis = await this.analyzeRouting(codebaseContents);

      console.log('Analyzing dependencies...');
      const dependencyAnalysis = await this.analyzeDependencies(codebaseContents);

      console.log('Analyzing configuration...');
      const configAnalysis = await this.analyzeConfiguration(codebaseContents);

      const codebaseAnalysis: CodebaseAnalysis = {
        routing: routingAnalysis,
        stateManagement: { type: 'unknown', storeLocations: [], complexity: 'low', suggestedApproach: '' },
        dataFetching: { patterns: [], apiEndpoints: [], suggestedNextjsApproach: [] },
        styling: { type: [], suggestedMigration: '' },
        dependencies: dependencyAnalysis,
        configuration: configAnalysis
      };

      return this.convertToAIAnalysis(codebaseAnalysis);
    } catch (error) {
      console.error('Error during AI analysis:', error);
      throw error;
    }
  }

  private async getRelevantFiles(): Promise<string[]> {
    const files = await glob('**/*.{js,jsx,ts,tsx}', { 
      cwd: this.projectPath, 
      ignore: ['**/node_modules/**', '**/dist/**'] 
    });
    return files;
  }

  private async readCodebaseFiles(files: string[]): Promise<{ [key: string]: string }> {
    const codebase: { [key: string]: string } = {};
    
    for (const file of files) {
      const filePath = path.join(this.projectPath, file);
      try {
        const content = await fs.readFile(filePath, 'utf-8');
        codebase[file] = content;
      } catch (error) {
        console.warn(`Warning: Could not read file ${file}:`, error);
      }
    }

    return codebase;
  }

  private async analyzeRouting(codebase: { [key: string]: string }): Promise<RoutingAnalysis> {
    const routingAnalysis = await this.anthropic.messages.create({
      model: "claude-3-opus-20240229",
      max_tokens: 4000,
      messages: [{
        role: "user",
        content: `Analyze the routing structure in this Vite/React codebase and suggest a Next.js migration path. Here's the codebase:\n\n${JSON.stringify(codebase, null, 2)}`
      }]
    });

    const content = routingAnalysis.content[0].text;

    return {
      type: this.detectRoutingType(codebase),
      routes: this.extractRoutes(codebase),
      suggestedNextjsStructure: this.parseSuggestedStructure(content),
      migrationSteps: this.parseMigrationSteps(content)
    };
  }

  private async analyzeDependencies(codebase: { [key: string]: string }): Promise<DependencyAnalysis> {
    const packageJson = JSON.parse(codebase['package.json'] || '{}');
    
    return {
      viteSpecific: this.findViteSpecificDeps(packageJson),
      nextCompatible: this.findNextCompatibleDeps(packageJson),
      requiresMigration: []
    };
  }

  private async analyzeConfiguration(codebase: { [key: string]: string }): Promise<ConfigurationAnalysis> {
    const configAnalysis = await this.anthropic.messages.create({
      model: "claude-3-opus-20240229",
      max_tokens: 2000,
      messages: [{
        role: "user",
        content: `Analyze the Vite configuration and suggest a Next.js configuration. Here's the codebase:\n\n${JSON.stringify(codebase, null, 2)}`
      }]
    });

    const content = configAnalysis.content[0].text;

    return {
      viteConfig: {
        plugins: [],
        aliases: {},
        environment: {},
        build: {}
      },
      environmentVariables: [],
      buildConfiguration: [],
      suggestedNextConfig: this.parseConfigSuggestion(content)
    };
  }

  private detectRoutingType(codebase: { [key: string]: string }): RoutingAnalysis['type'] {
    if (Object.keys(codebase).some(file => file.includes('react-router'))) {
      return 'react-router';
    }
    return 'unknown';
  }

  private extractRoutes(codebase: { [key: string]: string }): RouteInfo[] {
    // Simple route extraction logic - this could be enhanced
    return [];
  }

  private parseSuggestedStructure(content: string): string[] {
    // Parse the AI response to extract suggested structure
    return content.split('\n').filter(line => line.trim().startsWith('-'));
  }

  private parseMigrationSteps(content: string): string[] {
    // Parse the AI response to extract migration steps
    return content.split('\n').filter(line => /^\d+\./.test(line));
  }

  private findViteSpecificDeps(packageJson: any): string[] {
    const deps = { ...packageJson.dependencies, ...packageJson.devDependencies };
    return Object.keys(deps).filter(dep => dep.includes('vite') || dep.includes('rollup'));
  }

  private findNextCompatibleDeps(packageJson: any): string[] {
    const deps = { ...packageJson.dependencies, ...packageJson.devDependencies };
    return Object.keys(deps).filter(dep => !this.findViteSpecificDeps(packageJson).includes(dep));
  }

  private parseConfigSuggestion(content: string): string {
    // Extract the suggested next.config.js content from the AI response
    const configMatch = content.match(/```js\n([\s\S]*?)\n```/);
    return configMatch ? configMatch[1] : '';
  }

  private convertToAIAnalysis(analysis: CodebaseAnalysis): AIAnalysis {
    return {
      routing: {
        type: analysis.routing.type,
        routes: analysis.routing.routes,
        suggestedNextjsStructure: analysis.routing.suggestedNextjsStructure,
        migrationSteps: analysis.routing.migrationSteps
      },
      dependencies: {
        viteSpecific: analysis.dependencies.viteSpecific,
        nextCompatible: analysis.dependencies.nextCompatible,
        requiresMigration: []
      },
      configuration: {
        suggestedNextConfig: analysis.configuration.suggestedNextConfig
      }
    };
  }
} 