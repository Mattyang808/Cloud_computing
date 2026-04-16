from fabric import task

# ---- Config ----
PROJECT_DIR   = "/opt/wwc/mysites/lab"
VENV          = f"{PROJECT_DIR}/myvenv"
PY            = f"{VENV}/bin/python"
PIP           = f"{VENV}/bin/pip"
DJADMIN       = f"{VENV}/bin/django-admin"
NGINX_DEFAULT = "/etc/nginx/sites-enabled/default"

@task
def bootstrap(c):
    """Full setup: packages, project, polls app, repaired urls.py, migrations, nginx."""
    # System deps
    c.sudo("DEBIAN_FRONTEND=noninteractive apt-get update -y", pty=True)
    c.sudo("DEBIAN_FRONTEND=noninteractive apt-get upgrade -y", pty=True)
    c.sudo("DEBIAN_FRONTEND=noninteractive apt-get install -y python3-venv nginx", pty=True)

    # Project dir with correct ownership
    c.sudo("install -d -m 0755 -o ubuntu -g ubuntu /opt/wwc /opt/wwc/mysites /opt/wwc/mysites/lab", pty=True)

    # venv + Django
    c.run(f"test -d {VENV} || python3 -m venv {VENV}")
    c.run(f"{PIP} install -U pip django")

    # Django project + app (idempotent)
    c.run(f"cd {PROJECT_DIR} && test -f manage.py || {DJADMIN} startproject lab .")
    c.run(f"test -d {PROJECT_DIR}/polls || (cd {PROJECT_DIR} && {PY} manage.py startapp polls)")

    # polls files 
    c.run(f"""tee {PROJECT_DIR}/polls/views.py >/dev/null <<'PY'
from django.http import HttpResponse
def index(request):
    return HttpResponse("Hello, world.")
PY
""")
    c.run(f"""tee {PROJECT_DIR}/polls/urls.py >/dev/null <<'PY'
from django.urls import path
from . import views
urlpatterns = [ path("", views.index, name="index"), ]
PY
""")

    # write lab/urls.py
    c.run(f"""tee {PROJECT_DIR}/lab/urls.py >/dev/null <<'PY'
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('polls/', include('polls.urls')),
    path('admin/', admin.site.urls),
]
PY
""")

    # Django checks
    c.run(f"cd {PROJECT_DIR} && {PY} manage.py check")

    # Nginx reverse proxy
    c.sudo(f"""tee {NGINX_DEFAULT} >/dev/null <<'NG'
server {{
  listen 80 default_server;
  listen [::]:80 default_server;

  location / {{
    proxy_set_header Host 127.0.0.1;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_pass http://127.0.0.1:8000;
  }}
}}
NG
""", pty=True)
    c.sudo("nginx -t", pty=True)
    c.sudo("systemctl --no-ask-password restart nginx", pty=True)
    print("Bootstrap complete.")

@task
def runserver(c):
    print("Django is running at 127.0.0.1:8000 (proxied on :80).")
    c.run(f"test -f {PROJECT_DIR}/manage.py || (echo 'manage.py not found; run bootstrap first'; exit 1)")
    c.run("pkill -f 'manage.py runserver' || true", warn=True, pty=False)
    c.run(
        f"cd {PROJECT_DIR} && nohup {PY} manage.py runserver 127.0.0.1:8000 --noreload "
        f">/tmp/django.out 2>&1 & echo $! >/tmp/django.pid",
        pty=False
    )
    c.run(
        "sleep 1; ss -ltnp | grep ':8000' || "
        "(echo 'runserver failed; last logs:'; tail -n 200 /tmp/django.out; exit 1)",
        warn=False, pty=False
    )
    
@task
def clear(c):
    cmd = r"""
pids=""
[ -f /tmp/django.pid ] && pid=$(cat /tmp/django.pid 2>/dev/null || true) && [ -n "$pid" ] && pids="$pids $pid"
more=$(pgrep -f "manage.py runserver" 2>/dev/null || true)
[ -n "$more" ] && pids="$pids $more"
pids=$(echo $pids)
if [ -n "$pids" ]; then
  kill $pids 2>/dev/null || true
  sleep 0.5
  pgrep -f "manage.py runserver" >/dev/null && pkill -9 -f "manage.py runserver" || true
  rm -f /tmp/django.pid
  echo "Stopped Django (PIDs:$pids)"
else
  echo "No Django runserver processes are running."
fi
"""
    c.run(cmd, warn=True, hide=False, pty=False)

@task
def status(c):
    c.run("printf 'PID file: '; cat /tmp/django.pid 2>/dev/null || echo 'none'", pty=False)
    c.run("ss -ltnp | grep ':8000' || echo 'NOT_LISTENING'", pty=False)
    c.sudo("systemctl --no-pager status nginx || true", pty=True)

