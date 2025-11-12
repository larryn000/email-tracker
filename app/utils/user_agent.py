def parse_user_agent(user_agent_string):
    """
    Parse user agent string to extract device information

    Args:
        user_agent_string: HTTP User-Agent header value

    Returns:
        dict with device_type, browser, os
    """
    if not isinstance(user_agent_string, str) or not user_agent_string:
        return {
            'device_type': 'unknown',
            'browser': 'unknown',
            'os': 'unknown'
        }

    user_agent_lower = user_agent_string.lower()

    # Determine device type
    if any(mobile in user_agent_lower for mobile in ['mobile', 'android', 'iphone', 'ipod', 'blackberry', 'windows phone']):
        device_type = 'mobile'
    elif 'ipad' in user_agent_lower or 'tablet' in user_agent_lower:
        device_type = 'tablet'
    else:
        device_type = 'desktop'

    # Determine browser (order matters - check most specific first)
    browser = 'unknown'
    if 'edg' in user_agent_lower:
        browser = 'edge'
    elif 'chrome' in user_agent_lower:
        browser = 'chrome'
    elif 'safari' in user_agent_lower:
        browser = 'safari'
    elif 'firefox' in user_agent_lower:
        browser = 'firefox'
    elif 'opera' in user_agent_lower or 'opr' in user_agent_lower:
        browser = 'opera'

    # Determine OS (order matters for iOS detection)
    os_name = 'unknown'
    if 'windows' in user_agent_lower:
        os_name = 'windows'
    elif 'mac' in user_agent_lower:
        os_name = 'macos'
    elif 'linux' in user_agent_lower:
        os_name = 'linux'
    elif 'android' in user_agent_lower:
        os_name = 'android'
    elif 'ios' in user_agent_lower or 'iphone' in user_agent_lower or 'ipad' in user_agent_lower:
        os_name = 'ios'

    return {
        'device_type': device_type,
        'browser': browser,
        'os': os_name
    }