@echo off
REM Publish this project to GitHub (requires GitHub CLI: https://cli.github.com and "gh auth login" once).
setlocal
if "%OWNER%"=="" set OWNER=Milad-Shabani
if "%REPO%"=="" set REPO=early-attrition-analytics

where gh >nul 2>nul || (echo Install the GitHub CLI first: https://cli.github.com & exit /b 1)
if not exist .git git init -b main
git add -A
git diff --cached --quiet || git commit -m "chore: update project"

gh repo view %OWNER%/%REPO% >nul 2>nul
if errorlevel 1 (
  gh repo create %OWNER%/%REPO% --public --source=. --remote=origin --push --description "Censoring-aware early-attrition analytics with bilingual (EN/FA) HTML reports on a synthetic cohort"
) else (
  git remote get-url origin >nul 2>nul || git remote add origin https://github.com/%OWNER%/%REPO%.git
  git push -u origin main
)
gh repo edit %OWNER%/%REPO% --add-topic people-analytics --add-topic attrition --add-topic survival-analysis --add-topic python --add-topic data-visualization --add-topic hr-analytics
gh api -X POST repos/%OWNER%/%REPO%/pages -f build_type=workflow >nul 2>nul
echo Done: https://github.com/%OWNER%/%REPO%
endlocal
