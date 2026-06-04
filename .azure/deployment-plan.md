# CourseMatch Azure Deployment Plan

Status: Deployed

## Objective

Deploy the existing CourseMatch FastAPI backend from `fastapi-azure-lab` to the existing Azure App Service:

- Subscription: Azure for Students
- Resource group: RG_BIT312_quockhanh
- App Service: fastapi-2302700021
- Runtime target: Linux App Service, Python/FastAPI

No new Azure resources were created in this plan.

## Application Structure

- Backend: `fastapi-azure-lab`
- FastAPI app entrypoint: `main.py`
- ASGI object: `main:app`
- Frontend: `coursematch-frontend`
- Database: MongoDB Atlas via `MONGODB_URL`

The React frontend is built separately and served by the same FastAPI Azure App Service as static SPA assets.

## Backend Startup Command

```bash
gunicorn -w 2 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
```

## Required Backend App Settings

Secret values must not be printed to terminal or committed.

- `MONGODB_URL`
- `MONGODB_DB_NAME` or `DB_NAME`
- `JWT_SECRET_KEY`
- `JWT_ALGORITHM` or `ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `FRONTEND_URL`
- `ALLOWED_ORIGINS`
- `MAX_UPLOAD_SIZE_MB`

## Deployment Method

Use Azure CLI ZIP Deploy:

1. Build/compile backend locally.
2. Create a ZIP package from `fastapi-azure-lab`.
3. Exclude `.env`, `.venv`, logs, caches, and local build artifacts.
4. Configure startup command.
5. Configure App Settings from local `.env` without printing secret values.
6. Deploy ZIP to existing App Service.
7. Test production `/health`.
8. Test production `/docs`.

## Validation Steps

- `python -m compileall app`
- Confirm startup command is `main:app`
- Confirm local `/health` works
- Confirm MongoDB Atlas connection via local `/health`
- Confirm `.env` is not tracked by git
- Confirm `/docs` OpenAPI does not expose legacy form routes

## Risk Controls

- Do not create or delete Azure resources.
- Do not print MongoDB URI, JWT secret, token, or password.
- Do not commit `.env`.
- Do not re-enable legacy routes in Swagger.
- Do not change matching away from `binary_jaccard_ngram_v1`.

## Deployment Commands To Run After Approval

Commands will use the installed Azure CLI:

```powershell
& "C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd" webapp config set --resource-group RG_BIT312_quockhanh --name fastapi-2302700021 --startup-file "gunicorn -w 2 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000"
```

```powershell
& "C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd" webapp config appsettings set --resource-group RG_BIT312_quockhanh --name fastapi-2302700021 --settings @appsettings.json --output none
```

```powershell
& "C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd" webapp deploy --resource-group RG_BIT312_quockhanh --name fastapi-2302700021 --src-path <backend-zip-path> --type zip
```

## Result

- Backend deployed to: `https://fastapi-2302700021-gvfthwg8bxh0a4fr.southeastasia-01.azurewebsites.net`
- Frontend served from the same base URL.
- `/health`, `/docs`, and `/openapi.json` verified successfully after deployment.
- MongoDB Atlas connection verified through `/health`.
