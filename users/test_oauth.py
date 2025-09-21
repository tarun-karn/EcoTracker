from django.http import JsonResponse
from django.urls import reverse
from django.shortcuts import render


def test_oauth_urls(request):
    """Test view to check OAuth2 URL configuration"""
    try:
        # Test different URL patterns for google OAuth2
        url_patterns_to_try = [
            ('socialaccount_login', ['google']),
            ('socialaccount_signup', ['google']),
            ('google_oauth2_login', []),
            ('account_login', []),
        ]
        
        results = {}
        for pattern_name, args in url_patterns_to_try:
            try:
                url = reverse(pattern_name, args=args)
                results[pattern_name] = url
            except:
                results[pattern_name] = 'Not found'
        
        return JsonResponse({
            'status': 'success',
            'oauth_urls': results,
            'message': 'OAuth2 URL test completed'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error', 
            'error': str(e)
        })