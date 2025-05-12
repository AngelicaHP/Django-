from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from core.views import home
from accounts.views import login_view, logout_view
from django.urls import path, include


urlpatterns = [
 path('admin/', admin.site.urls),
 path('', login_required(home), name='home'),
 # URLs de autenticación
 path('login/', login_view, name='login'),
 path('logout/', logout_view, name='logout'),

 # Incluir URLs de apps
 path('accounts/', include('accounts.urls')),
 path('core/', include('core.urls')),

 path('accounts/', include('allauth.urls')), # URLs para allauth
]
if settings.DEBUG:
 urlpatterns += static(settings.STATIC_URL,
document_root=settings.STATIC_ROOT)
 urlpatterns += static(settings.MEDIA_URL,
document_root=settings.MEDIA_ROOT)