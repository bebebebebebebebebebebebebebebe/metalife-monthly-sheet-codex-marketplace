# MetaLife Monthly Sheet Codex Marketplace

This repository publishes a Codex plugin marketplace for the `metalife-monthly-sheet` workflow.

The plugin helps Codex parse MetaLife timecard CSV exports and safely update an existing monthly Google Sheets report while preserving headers, formulas, formatting, validations, dimensions, and summary cells.

## Structure

- `.agents/plugins/marketplace.json` registers the marketplace entry.
- `plugins/metalife-monthly-sheet/.codex-plugin/plugin.json` defines the plugin metadata.
- `plugins/metalife-monthly-sheet/skills/metalife-monthly-sheet/` contains the reusable Codex skill.

## Usage

Connect or clone this repository in Codex and point Codex at `.agents/plugins/marketplace.json` as the marketplace definition.

The workflow requires:

- A MetaLife timecard CSV export.
- A target Google Sheets URL or spreadsheet ID.
- Access to Google Sheets through the available Codex Google Drive or Sheets tools.

No real CSV exports, spreadsheet URLs, credentials, or personal timecard data are stored in this repository.

