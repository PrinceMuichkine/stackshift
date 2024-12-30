#!/usr/bin/env node

import { Command } from 'commander';
import chalk from 'chalk';
import inquirer from 'inquirer';
import { ProjectAnalyzer } from './utils/projectAnalyzer';
import { MigrationPlanner } from './utils/migrationPlanner';
import path from 'path';
import dotenv from 'dotenv';
import { CodebaseAnalysis } from './types';
import fs from 'fs-extra';
import { generateMigrationReport } from './utils/reportGenerator';
import { MigrationResult } from './types';

dotenv.config();

const program = new Command();

program
  .name('stackshift')
  .description('CLI tool to help migrate from Vite to Next.js')
  .version('0.1.0');

const analyzeCommand = new Command('analyze')
  .argument('[projectPath]', 'Path to the project to analyze')
  .option('--no-ai', 'Skip AI analysis')
  .option('-c, --config <files...>', 'Custom configuration files to include in analysis')
  .option('--no-interactive', 'Skip interactive prompts')
  .action(async (projectPath, options) => {
    try {
      if (!options.ai && !process.env.ANTHROPIC_API_KEY) {
        console.log(chalk.yellow('Warning: No Anthropic API key found. Running without AI analysis.'));
        options.ai = false;
      }

      const resolvedPath = projectPath || '.';

      console.log(chalk.blue('Analyzing project structure...'));
      
      const analyzer = new ProjectAnalyzer(path.resolve(resolvedPath));
      const analysis = await analyzer.analyzeProject({
        config: options.config,
        skipAI: !options.ai,
        nonInteractive: !options.interactive
      });
      
      console.log(chalk.green('\nAnalysis complete! ✨\n'));
      console.log(chalk.yellow('Project Details:'));
      console.log('Framework:', analysis.framework);
      console.log('Dependencies:', analysis.dependencies.length);
      console.log('TypeScript Config:', analysis.tsConfig);
      console.log('Python Config:', analysis.pythonConfig);
      console.log('Test Config:', analysis.testConfig);
      console.log('Lint Config:', analysis.lintConfig);
      console.log('Prettier Config:', analysis.prettierConfig);
      console.log('CI Config:', analysis.ciConfig);
      console.log('Containerization Config:', analysis.containerizationConfig);

      if (analysis.aiSuggestions) {
        console.log(chalk.cyan('\nDetailed Migration Analysis:\n'));
        
        // Routing
        console.log(chalk.yellow('📁 Routing Migration:'));
        console.log('Type:', analysis.aiSuggestions.routing.type);
        console.log('Suggested Next.js Structure:');
        analysis.aiSuggestions.routing.suggestedNextjsStructure.forEach((step: string) => 
          console.log(`  - ${step}`));

        // Dependencies
        console.log(chalk.yellow('\n📦 Dependencies:'));
        console.log('To Remove:');
        analysis.aiSuggestions.dependencies.viteSpecific.forEach((dep: string) => 
          console.log(`  - ${dep}`));
        console.log('To Add:');
        analysis.aiSuggestions.dependencies.nextCompatible.forEach((dep: string) => 
          console.log(`  - ${dep}`));

        // Configuration
        console.log(chalk.yellow('\n⚙️ Configuration:'));
        console.log('Suggested next.config.js:');
        console.log(analysis.aiSuggestions.configuration.suggestedNextConfig);

        // Migration Steps
        console.log(chalk.green('\n🚀 Migration Steps:'));
        analysis.aiSuggestions.routing.migrationSteps.forEach((step: string, index: number) => 
          console.log(`${index + 1}. ${step}`));

        // Save detailed report
        const reportPath = path.join(process.cwd(), 'migration-report.md');
        fs.writeFileSync(reportPath, generateMigrationReport(analysis.aiSuggestions));
        console.log(chalk.blue(`\n📝 Detailed migration report saved to ${reportPath}`));
      }
    } catch (error) {
      console.error(chalk.red('Error analyzing project:'), error);
      process.exit(1);
    }
  });

const migrateCommand = new Command('migrate')
  .description('Migrate the project from Vite to Next.js')
  .option('--no-interactive', 'Skip interactive prompts')
  .action(async (options) => {
    console.log('Migration feature coming soon!');
  });

program.addCommand(analyzeCommand);
program.addCommand(migrateCommand);

program.on('command:*', function () {
  console.error('Invalid command: %s\nSee --help for a list of available commands.', program.args.join(' '));
  process.exit(1);
});

program.parse(process.argv);

// Display progress bar during migration
function renderProgressBar(current: number, total: number) {
  const width = 40;
  const ratio = current / total;
  const filled = Math.floor(width * ratio);
  const empty = width - filled;

  const filledPart = '█'.repeat(filled);
  const emptyPart = '░'.repeat(empty);

  process.stdout.write(`\r[${filledPart}${emptyPart}] ${Math.floor(ratio * 100)}%`);
}

// Provide a summary report
function displayMigrationSummary(migrationResult: MigrationResult) {
  console.log(chalk.green('\nMigration Summary:'));
  console.log(`Migrated files: ${migrationResult.migratedFiles}`);
  console.log(`Skipped files: ${migrationResult.skippedFiles}`);
  console.log(`Warnings: ${migrationResult.warnings.length}`);
  console.log(`Errors: ${migrationResult.errors.length}`);

  if (migrationResult.warnings.length > 0) {
    console.log(chalk.yellow('\nMigration Warnings:'));
    migrationResult.warnings.forEach((warning: string) => console.log(`- ${warning}`));
  }

  if (migrationResult.errors.length > 0) {
    console.log(chalk.red('\nMigration Errors:'));
    migrationResult.errors.forEach((error: string) => console.log(`- ${error}`));
  }
} 