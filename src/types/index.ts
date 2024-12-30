export interface MigrationPlan {
  steps: MigrationStep[];
  estimatedTime: string;
  estimatedCost: number;
  complexity: 'Low' | 'Medium' | 'High';
}

export interface MigrationStep {
  id: string;
  title: string;
  description: string;
  tasks: Task[];
  estimatedTime: string;
}

export interface Task {
  id: string;
  description: string;
  codeChanges?: string;
  resources?: string[];
}

export interface ProjectAnalysis {
  framework: string;
  dependencies: Dependency[];
  tsConfig: string | null;
  pythonConfig: string | null;
  testConfig: string | null;
  lintConfig: string | null;
  prettierConfig: string | null;
  ciConfig: string | null;
  containerizationConfig: string | null;
  routingStructure: string[];
  aiSuggestions?: AIAnalysis;
}

export interface Dependency {
  name: string;
  version: string;
  isCompatible: boolean;
  alternativePackage?: string;
}

export interface AIAnalysis {
  routing: {
    type: string;
    routes: RouteInfo[];
    suggestedNextjsStructure: string[];
    migrationSteps: string[];
  };
  dependencies: {
    viteSpecific: string[];
    nextCompatible: string[];
    requiresMigration: string[];
  };
  configuration: {
    suggestedNextConfig: string;
  };
}

export interface CodebaseAnalysis {
  routing: RoutingAnalysis;
  stateManagement: StateManagementAnalysis;
  dataFetching: DataFetchingAnalysis;
  styling: StylingAnalysis;
  dependencies: DependencyAnalysis;
  configuration: ConfigurationAnalysis;
}

export interface RoutingAnalysis {
  type: 'react-router' | 'reach-router' | 'custom' | 'unknown';
  routes: RouteInfo[];
  suggestedNextjsStructure: string[];
  migrationSteps: string[];
}

export interface RouteInfo {
  path: string;
  component: string;
  hasParams: boolean;
  hasQueryParams: boolean;
  hasLoaders?: boolean;
}

export interface StateManagementAnalysis {
  type: 'redux' | 'zustand' | 'context' | 'recoil' | 'jotai' | 'unknown';
  storeLocations: string[];
  complexity: 'low' | 'medium' | 'high';
  suggestedApproach: string;
}

export interface DataFetchingAnalysis {
  patterns: ('rest' | 'graphql' | 'swr' | 'react-query' | 'custom')[];
  apiEndpoints: string[];
  suggestedNextjsApproach: string[];
}

export interface StylingAnalysis {
  type: ('css-modules' | 'styled-components' | 'emotion' | 'tailwind' | 'sass')[];
  suggestedMigration: string;
}

export interface DependencyAnalysis {
  viteSpecific: string[];
  nextCompatible: string[];
  requiresMigration: {
    dependency: string;
    reason: string;
    suggestion: string;
  }[];
}

export interface ConfigurationAnalysis {
  viteConfig: ViteConfigAnalysis;
  environmentVariables: string[];
  buildConfiguration: string[];
  suggestedNextConfig: string;
}

export interface ViteConfigAnalysis {
  plugins: string[];
  aliases: Record<string, string>;
  environment: Record<string, string>;
  build: Record<string, any>;
}

export interface MigrationResult {
  migratedFiles: number;
  skippedFiles: number;
  warnings: string[];
  errors: string[];
}

export interface ProjectAnalyzerOptions {
  config?: string[];
  skipAI?: boolean;
  nonInteractive?: boolean;
} 