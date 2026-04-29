# Deploy frontend to Vercel

The frontend in `app/` is a Vite SPA with React Router. The repo ships a `vercel.json` that pins the framework, output dir, and the catch-all rewrite required for client-side routes.

## One-time setup

```bash
npm install -g vercel
vercel login                       # opens browser for OAuth
```

## First deploy

```bash
cd app
vercel                             # creates the project (interactive prompts)
```

When prompted:
- **Set up and deploy?** Yes
- **Which scope?** Your personal account
- **Link to existing project?** No
- **Project name?** `migration-atlas`
- **Directory?** `./` (you're already in `app/`)
- **Override settings?** No (the `vercel.json` covers it)

Vercel deploys to a preview URL. Verify, then promote:

```bash
vercel --prod
```

## Configuring the backend URL

Frontend reaches the backend via `VITE_API_URL`. In dev, the Vite proxy forwards `/api/*` to `localhost:8000`. In prod, set the env var in the Vercel dashboard:

```
VITE_API_URL=https://<your-handle>-migration-atlas.hf.space
```

After setting, redeploy:
```bash
vercel --prod
```

## Continuous deploy from GitHub

Once the Vercel project is linked to the GitHub repo (`ujjawal40/migration-atlas`), every push to `main` redeploys automatically. Pull requests get preview URLs.

## CORS

The HF Spaces backend reads `CORS_ORIGINS` from its environment. Add your Vercel URL there:

```
CORS_ORIGINS=https://migration-atlas.vercel.app,https://migration-atlas-<hash>.vercel.app
```
