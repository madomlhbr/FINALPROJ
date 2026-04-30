from django.shortcuts import redirect 
from django.conf import settings 
  
  
class LoginRequiredMiddleware: 
    """Forces login for every view except the login/logout pages.""" 
  
    # These URLs are allowed without authentication 
    EXEMPT_URLS = { 
        settings.LOGIN_URL.rstrip("/"),  # /login/ 
        "/logout", 
        "/admin",       # Django admin handles its own auth 
        "/admin/login", 
    } 
  
    def __init__(self, get_response): 
        self.get_response = get_response 
  
    def __call__(self, request): 
        path = request.path_info.rstrip("/") 
        is_exempt = any( 
            path == url or path.startswith(url + "/") 
            for url in self.EXEMPT_URLS 
        ) 
  
        if not request.user.is_authenticated and not is_exempt: 
            return redirect(settings.LOGIN_URL + f"?next={request.path}") 
  
        return self.get_response(request)