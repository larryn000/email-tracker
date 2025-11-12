"""
Unit tests for user agent parsing utility functions

These are pure unit tests - they test individual functions in isolation
without any database or web framework dependencies.
"""

import pytest
from app.utils.user_agent import parse_user_agent


class TestParseUserAgent:
    """Test user agent string parsing function"""

    # Desktop browsers
    def test_chrome_windows(self):
        """Test parsing Chrome on Windows"""
        ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        result = parse_user_agent(ua)
        assert result['device_type'] == 'desktop'
        assert result['browser'] == 'chrome'
        assert result['os'] == 'windows'

    def test_firefox_linux(self):
        """Test parsing Firefox on Linux"""
        ua = 'Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0'
        result = parse_user_agent(ua)
        assert result['device_type'] == 'desktop'
        assert result['browser'] == 'firefox'
        assert result['os'] == 'linux'

    def test_safari_macos(self):
        """Test parsing Safari on macOS"""
        ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
        result = parse_user_agent(ua)
        assert result['device_type'] == 'desktop'
        assert result['browser'] == 'safari'
        assert result['os'] == 'macos'

    def test_edge_windows(self):
        """Test parsing Edge on Windows"""
        ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59'
        result = parse_user_agent(ua)
        assert result['device_type'] == 'desktop'
        assert result['browser'] == 'edge'
        assert result['os'] == 'windows'

    def test_opera_windows(self):
        """Test parsing Opera on Windows"""
        ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 OPR/77.0.4054.203'
        result = parse_user_agent(ua)
        assert result['device_type'] == 'desktop'
        assert result['browser'] == 'opera'
        assert result['os'] == 'windows'

    # Mobile devices
    def test_chrome_android(self):
        """Test parsing Chrome on Android"""
        ua = 'Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36'
        result = parse_user_agent(ua)
        assert result['device_type'] == 'mobile'
        assert result['browser'] == 'chrome'
        assert result['os'] == 'android'

    def test_safari_iphone(self):
        """Test parsing Safari on iPhone"""
        ua = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1'
        result = parse_user_agent(ua)
        assert result['device_type'] == 'mobile'
        assert result['browser'] == 'safari'
        assert result['os'] == 'ios'

    def test_safari_ipad(self):
        """Test parsing Safari on iPad (tablet)"""
        ua = 'Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
        result = parse_user_agent(ua)
        assert result['device_type'] == 'tablet'
        assert result['browser'] == 'safari'
        assert result['os'] == 'ios'

    def test_chrome_tablet(self):
        """Test parsing Chrome on Android tablet"""
        ua = 'Mozilla/5.0 (Linux; Android 11; SM-T870) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Safari/537.36'
        result = parse_user_agent(ua)
        # Has Android and "tablet" keyword
        assert result['device_type'] == 'tablet'
        assert result['browser'] == 'chrome'
        assert result['os'] == 'android'

    # Edge cases
    def test_empty_string(self):
        """Test parsing empty string"""
        result = parse_user_agent('')
        assert result['device_type'] == 'unknown'
        assert result['browser'] == 'unknown'
        assert result['os'] == 'unknown'

    def test_none_value(self):
        """Test parsing None value"""
        result = parse_user_agent(None)
        assert result['device_type'] == 'unknown'
        assert result['browser'] == 'unknown'
        assert result['os'] == 'unknown'

    def test_invalid_type_number(self):
        """Test parsing with number instead of string"""
        result = parse_user_agent(123)
        assert result['device_type'] == 'unknown'
        assert result['browser'] == 'unknown'
        assert result['os'] == 'unknown'

    def test_invalid_type_dict(self):
        """Test parsing with dict instead of string"""
        result = parse_user_agent({'ua': 'test'})
        assert result['device_type'] == 'unknown'
        assert result['browser'] == 'unknown'
        assert result['os'] == 'unknown'

    def test_unknown_user_agent(self):
        """Test parsing unknown/custom user agent"""
        result = parse_user_agent('CustomBot/1.0')
        assert result['device_type'] == 'desktop'  # Default when no mobile indicators
        assert result['browser'] == 'unknown'
        assert result['os'] == 'unknown'

    def test_case_insensitive(self):
        """Test that parsing is case-insensitive"""
        ua_lower = 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 chrome/91.0.4472.124 safari/537.36'
        ua_upper = 'MOZILLA/5.0 (WINDOWS NT 10.0; WIN64; X64) APPLEWEBKIT/537.36 CHROME/91.0.4472.124 SAFARI/537.36'

        result_lower = parse_user_agent(ua_lower)
        result_upper = parse_user_agent(ua_upper)

        assert result_lower == result_upper

    # Browser detection order (Edge should be detected before Chrome)
    def test_edge_detected_before_chrome(self):
        """Test that Edge is correctly detected even though UA contains 'chrome'"""
        ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59'
        result = parse_user_agent(ua)
        # Should detect as Edge, not Chrome
        assert result['browser'] == 'edge'

    def test_mobile_keywords(self):
        """Test various mobile keywords"""
        mobile_keywords = ['mobile', 'android', 'iphone', 'ipod', 'blackberry', 'windows phone']

        for keyword in mobile_keywords:
            ua = f'CustomAgent/{keyword}/1.0'
            result = parse_user_agent(ua)
            assert result['device_type'] == 'mobile', f'Failed for keyword: {keyword}'

    def test_windows_phone(self):
        """Test Windows Phone detection"""
        ua = 'Mozilla/5.0 (Windows Phone 10.0; Android 6.0.1; Microsoft; Lumia 950) AppleWebKit/537.36 Chrome/52.0.2743.116 Mobile Safari/537.36 Edge/15.14977'
        result = parse_user_agent(ua)
        assert result['device_type'] == 'mobile'
        assert result['browser'] == 'edge'

    def test_blackberry(self):
        """Test BlackBerry detection"""
        ua = 'Mozilla/5.0 (BlackBerry; U; BlackBerry 9900; en) AppleWebKit/534.11+ Version/7.1.0.346 Mobile Safari/534.11+'
        result = parse_user_agent(ua)
        assert result['device_type'] == 'mobile'
