# Frontend Application

## Important Note on Installation
If you encounter any errors when running `npm install` (especially peer dependency issues regarding React 19), please run the following command instead:

```bash
npm install --legacy-peer-deps
```

This will bypass strict peer dependency checks which sometimes incorrectly flag valid React 19 / Next.js 16 setups with third-party libraries.
