import { Command } from 'commander';
import chalk from 'chalk';
import inquirer from 'inquirer';
import path from 'path';
import fs from 'fs-extra';
import { ProjectAnalyzer } from '../utils/projectAnalyzer';
import { transformViteConfig } from '../transformers/viteConfig';
import { transformRoutes } from '../transformers/routes';
import { transformPackageJson } from '../transformers/packageJson';
import { CodebaseAnalysis } from '../types';
import { MigrationPlanner } from '../utils/migrationPlanner';
import { MigrationPlan } from '../types';

export function createMigrateCommand(): Command {
  const command = new Command('migrate');
  
  command
    .description('Start the migration process')
    .option('-y, --yes', 'Skip confirmation prompts')
    .option('-d, --dry-run', 'Show what would be migrated without making changes')
    .action(async (options) => {
      try {
        // Get project path
        const { projectPath } = await inquirer.prompt([
          {
            type: 'input',
            name: 'projectPath',
            message: 'Enter the path to your Vite project:',
            default: '.',
          }
        ]);

        // Analyze project
        console.log(chalk.blue('Analyzing project...'));
        const analyzer = new ProjectAnalyzer(path.resolve(projectPath));
        const analysis = await analyzer.analyzeProject();

        // Generate migration plan
        const planner = new MigrationPlanner(analysis);
        const migrationPlan = planner.generateMigrationPlan();

        if (!options.yes) {
          const { confirm } = await inquirer.prompt([
            {
              type: 'confirm',
              name: 'confirm',
              message: 'Ready to start migration? This will modify your project files.',
              default: false,
            }
          ]);

          if (!confirm) {
            console.log(chalk.yellow('Migration cancelled'));
            return;
          }
        }

        // Create backup
        const backupDir = path.join(projectPath, '.migration-backup');
        if (!options.dryRun) {
          await fs.copy(projectPath, backupDir, {
            filter: (src) => !src.includes('node_modules')
          });
        }

        // Perform migrations
        await performMigration(projectPath, migrationPlan, options.dryRun);

        console.log(chalk.green('\nMigration completed! ✨'));
        console.log(chalk.blue(`Backup created at: ${backupDir}`));
        console.log(chalk.yellow('\nNext steps:'));
        console.log('1. Review the changes');
        console.log('2. Run npm install');
        console.log('3. Start the Next.js development server');

      } catch (error) {
        console.error(chalk.red('Error during migration:'), error);
        process.exit(1);
      }
    });

  return command;
}

async function performMigration(
  projectPath: string,
  migrationPlan: MigrationPlan,
  dryRun: boolean
) {
  for (const step of migrationPlan.steps) {
    console.log(chalk.blue(`\n${step.title}...`));

    for (const task of step.tasks) {
      console.log(`- ${task.description}`);

      if (!dryRun && task.codeChanges) {
        // Apply code changes
        // ... implementation ...
      }
    }
  }
} 