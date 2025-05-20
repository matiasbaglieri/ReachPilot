# CSV Imports for Contact Upload

This folder is used for storing CSV files that are imported to upload contacts into the database.

## CSV Format

Each CSV file should contain the following columns:

- `email` (required)
- `first_name` (required)
- `last_name` (required)
- `company_linkedin` (optional)
- `title` (optional)
- `city` (optional)
- `country` (optional)
- `website` (optional)
- `linkedin` (optional)

## How to Import

1. Place your CSV file in this `dumps/` directory.
2. Use the provided import script or tool in the project to read the CSV and insert contacts into the database.
3. Ensure your CSV file does not contain duplicate emails, as the `email` field must be unique.

## Example

```csv
email,first_name,last_name,company_linkedin,title,city,country,website,linkedin
john.doe@example.com,John,Doe,ExampleCompany,Manager,London,UK,www.example.com,https://linkedin.com/in/johndoe
jane.smith@example.com,Jane,Smith,AnotherCompany,Director,Manchester,UK,www.another.com,https://linkedin.com/in/janesmith
```

## Notes

- Only `.csv` files should be placed in this directory.
- This directory is excluded from version control via `.gitignore`.