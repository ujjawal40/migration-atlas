# Deploy frontend to Vercel

Vercel is free, zero-config, and built for React. The frontend in `app/` deploys cleanly.

## Steps

1. **Install the Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Push the repo to GitHub** (Vercel auto-detects).

3. **Import the project** at [vercel.com/new](https://vercel.com/new):
   - Root directory: `app/`
   - Framework preset: detected automatically (Vite or Next.js)
   - Build command: `npm run build`
   - Output directory: `dist/` (Vite) or `.next/` (Next.js)

4. **Set environment variables** in the Vercel dashboard:
   ```
   VITE_API_URL=https://your-backend.hf.space
   ```

5. **Deploy**:
   ```bash
   cd app && vercel --prod
   ```

Vercel gives you a `*.vercel.app` URL automatically. Custom domain optional.

## Pointing to the backend

The frontend hits the backend's `/query` endpoint. In production, this is the HF Spaces URL from [the backend deploy guide](hf-spaces.md). Set `VITE_API_URL` accordingly.

## CORS

Make sure the backend's `CORS_ORIGINS` env var includes your Vercel URL.
