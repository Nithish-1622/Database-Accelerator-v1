MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB
ALLOWED_FILE_TYPES = ['csv', 'xlsx', 'xls', 'json']
MIN_FILE_SIZE = 100  # 100 bytes


def validate_file(file):
    """
    Validate uploaded file
    Returns: {
        'valid': bool,
        'message': str
    }
    """
    
    # Check file size
    if file.size > MAX_FILE_SIZE:
        return {
            'valid': False,
            'message': f'File size exceeds maximum allowed size of {MAX_FILE_SIZE / (1024 * 1024):.0f} MB'
        }
    
    if file.size < MIN_FILE_SIZE:
        return {
            'valid': False,
            'message': f'File size is too small. Minimum size is {MIN_FILE_SIZE} bytes'
        }
    
    # Check file type
    filename = file.name
    file_ext = filename.split('.')[-1].lower()
    
    if file_ext not in ALLOWED_FILE_TYPES:
        return {
            'valid': False,
            'message': f'File type {file_ext} not supported. Allowed types: {", ".join(ALLOWED_FILE_TYPES)}'
        }
    
    return {
        'valid': True,
        'message': 'File validation passed'
    }
