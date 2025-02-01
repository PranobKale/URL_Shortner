from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse,HttpResponse
from .models import URL, AccessLog
from hashlib import md5
import datetime
from django.utils.timezone import now


def index(request):
    return render(request, 'shortener/index.html')
    # return HttpResponse("<h1> Hello $$$$ </h1>")

full_shortened_url = ''

def shorten_url(request):
    """
    Shortens a given URL and stores it in the database with an expiration timestamp.

    Description:
    This function accepts a POST request containing an `original_url` and an optional `expiry` parameter
    (defaulting to 24 hours). It generates a unique shortened URL using an MD5 hash of the original URL.
    If the same original URL has already been shortened, it retrieves the existing shortened URL.
    The function returns a rendered HTML page displaying the shortened URL.

    Parameters:
    - request: The HTTP request object.

    Returns:
    - A rendered HTML page with the shortened URL if the operation succeeds.
    - A JSON error response if there is an issue with the input or unexpected errors occur.
    """
    try:
        # Check if the request method is POST
        if request.method == 'POST':
            global full_shortened_url
            # Extract the original URL and expiry time from the request
            original_url = request.POST.get('url')
            expiry_hours = request.POST.get('expiry', 24)  # Default expiry is 24 hours if not provided
            if isinstance(expiry_hours,str):
                expiry_hours = 24
            else:
                expiry_hours = int(expiry_hours)
            
            # Validate the input URL
            if not original_url:
                raise ValueError("Original URL is required.")  # Raise an error if the URL is missing
            
            # Generate a unique hash for the URL
            hash_object = md5(original_url.encode())
            short_url = hash_object.hexdigest()[:6]  # Use the first 6 characters of the hash as the short code

            # Create or retrieve the URL object in the database
            url, created = URL.objects.get_or_create(
                original_url=original_url,
                defaults={
                    'shortened_url': short_url,  # Store the generated short URL
                    'expiration_timestamp': datetime.datetime.now() + datetime.timedelta(hours=expiry_hours)  # Set expiration
                }
            )

            # Dynamically generate the full shortened URL using request.build_absolute_uri
            full_shortened_url = request.build_absolute_uri(f'/{url.shortened_url}/')

            data = {
                'shortened_url': full_shortened_url,  # Full shortened URL
                'shortened_url_code': url.shortened_url  # Shortened URL code for internal usage
            }

            # Render the response using the 'shortened_url.html' template
            return render(request, 'shortener/shortened_url.html', context=data)
        
        else:
            # Handle non-POST requests
            return JsonResponse({'error': 'Invalid request method. Please use POST.'}, status=400)
    
    except ValueError as ve:
        # Handle validation errors (e.g., missing original URL)
        return JsonResponse({'error': str(ve)}, status=400)
    
    except Exception as e:
        # Handle all other unexpected exceptions
        return JsonResponse({'error': 'An unexpected error occurred.', 'details': str(e)}, status=500)

def redirect_to_original(request, short_url):
    """
    Redirects a shortened URL to its original URL.

    Parameters:
    - request: The HTTP request object.
    - short_url: The shortened URL code.

    Returns:
    - Redirects to the original URL or an appropriate error response.
    """
    try:
        print(f"Redirecting short URL: {short_url}")

        # Fetch the URL object using the shortened URL
        url = get_object_or_404(URL, shortened_url=short_url)

        # Check if the URL has expired
        if url.expiration_timestamp < now():
            return HttpResponse("The URL has expired.", status=410)

        # Log the access for analytics, including the timestamp, IP address, and shortened URL
        access_timestamp = datetime.datetime.now()  # Get the current timestamp
        AccessLog.objects.create(
            shortened_url=url,
            ip_address=request.META.get('REMOTE_ADDR'),
            access_timestamp=access_timestamp 
        )
        # Redirect to the original URL
        return redirect(url.original_url)
    except Exception as e:
        # Return a detailed error message if something goes wrong
        return HttpResponse(f"Error: Unable to redirect. Details: {e}, Short URL: {short_url}", status=404)


def analytics(request, short_url):
    """
    Provides analytics for a shortened URL.

    Parameters:
    - request: The HTTP request object.
    - short_url: The shortened URL code.

    Returns:
    - Renders the analytics page with URL access logs and details.
    """
    try:
        print(f"Fetching analytics for short URL: {short_url}")

        # Fetch the URL object using the shortened URL
        url = get_object_or_404(URL, shortened_url=short_url)

        # Fetch access logs for the shortened URL
        logs = url.access_logs.all()
    
        # Prepare data for rendering
        data = {
            'short_url': f'{full_shortened_url}',  # Full shortened URL
            'access_count': logs.count(),  # Total number of accesses
            'expiration_timestamp': url.expiration_timestamp,  # Expiry date and time
            'original_url': url.original_url,  # Original URL
            'access_logs': [
                {'timestamp': log.access_timestamp, 'ip_address': log.ip_address}
                for log in logs
            ]  # List of access log details
        }

        # Render the analytics page
        return render(request, 'shortener/analytics.html', context=data)
    except Exception as e:
        # Handle unexpected errors and return a detailed error response
        return JsonResponse(
            {'error': f"An error occurred while fetching analytics. Details: {e}"},
            status=500
        )
