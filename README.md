# Lythhammad.github.io

FUNCTION handle_login_request(username, password): 

    input_sanitized = SANITIZE(username, password) 
    user = DATABASE.find_user(input_sanitized.username) 
    
    IF user AND VERIFY_PASSWORD(input_sanitized.password, user.password_hash): 
        session_token = GENERATE_SECURE_TOKEN() 
        SET_SECURE_HTTP_ONLY_COOKIE(session_token) 
        RETURN HTTP_200_OK(dashboard_data) 

    ELSE: 
        LOG_FAILED_ATTEMPT(input_sanitized.username) 
        RETURN HTTP_401_UNAUTHORIZED("Invalid credentials")   

FUNCTION fetch_portfolio_data(): 

    languages = DATABASE.get_learned_languages() 
    projects = DATABASE.get_projects() 
    RETURN JSON({ "languages": languages, "projects": projects }) 

 
