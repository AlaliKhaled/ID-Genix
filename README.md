# 🚀 ID-Genix AI Tech Portal

ID-Genix is a high-end, responsive web platform tailored for AI-powered applications, tech infrastructure services, and massive data processing. The UI/UX is built specifically with modern glassmorphism tech visuals and a cohesive neural particle background suited for high-tier agency portfolios.

## 📥 Required Files & Deployment
This project is fully packaged and ready to be deployed entirely via git push onto providers such as **Render**, **Heroku**, or **Railway** seamlessly without additional source code configuration.

### Local Initialization
1. Ensure Python 3.x is installed. Create a virtual environment using `python -m venv venv` and activate it.
2. run `pip install -r requirements.txt` to gather server dependencies (Flask & SQLAlchemy).
3. Boot the local server gracefully via `python app.py` or use gunicorn with `gunicorn app:app`.

### Control Panel & Dashboard Configuration
- **Default Backdoor URL:** `/login` or `/admin-portal-secure-88`
- **Default Auth Name:** `admin`
- **Default Key:** `123456`

> [!WARNING]
> Please change default credentials!

### Environment Variables 
The backend has securely abstracted away hardcoded variables. You must enter these variables in your host deployment console. 
- `SECRET_KEY`: A highly complex entropy string (E.g generated using `python -c "import secrets; print(secrets.token_hex(24))"`)
- `ADMIN_USER`: Set your personal login handle.
- `ADMIN_PASS`: Set your bulletproof login password.
- `DATABASE_URL`: (Optional) Use this to hook the application directly to a PostgreSQL container inside Render. (The system will revert to a local scalable `sqlite` file without it).
- `MAIL_USERNAME` & `MAIL_PASSWORD`: Input credentials here so the platform can email you in real-time instantly when any consumer requests a tech project.
