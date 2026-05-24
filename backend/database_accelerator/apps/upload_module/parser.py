import pandas as pd
import io
import uuid
from openpyxl import load_workbook

def parse_file(file):
    """
    Parse uploaded file and extract metadata
    Returns: {
        'success': bool,
        'dataset_id': str,
        'file_type': str,
        'rows': int,
        'columns': int,
        'column_names': list,
        'column_types': dict,
        'message': str (if error)
    }
    """
    try:
        filename = file.name
        file_ext = filename.split('.')[-1].lower()
        dataset_id = str(uuid.uuid4())

        if file_ext == 'csv':
            result = parse_csv(file)
        elif file_ext in ['xlsx', 'xls']:
            result = parse_excel(file)
        elif file_ext == 'json':
            result = parse_json(file)
        else:
            return {
                'success': False,
                'message': f'Unsupported file format: {file_ext}. Supported: CSV, XLSX, JSON'
            }
        
        if result['success']:
            result['dataset_id'] = dataset_id
        
        return result

    except Exception as e:
        return {
            'success': False,
            'message': f'Error parsing file: {str(e)}'
        }


def parse_csv(file):
    """Parse CSV file"""
    try:
        # Read CSV file
        df = pd.read_csv(file)
        
        return {
            'success': True,
            'file_type': 'csv',
            'rows': len(df),
            'columns': len(df.columns),
            'column_names': df.columns.tolist(),
            'column_types': infer_column_types(df)
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Error parsing CSV: {str(e)}'
        }


def parse_excel(file):
    """Parse Excel file"""
    try:
        # Read Excel file
        df = pd.read_excel(file)
        
        return {
            'success': True,
            'file_type': 'xlsx',
            'rows': len(df),
            'columns': len(df.columns),
            'column_names': df.columns.tolist(),
            'column_types': infer_column_types(df)
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Error parsing Excel: {str(e)}'
        }


def parse_json(file):
    """Parse JSON file (tabular format)"""
    try:
        # Read JSON file
        file.seek(0)
        content = file.read().decode('utf-8')
        data = pd.read_json(io.StringIO(content))
        
        return {
            'success': True,
            'file_type': 'json',
            'rows': len(data),
            'columns': len(data.columns),
            'column_names': data.columns.tolist(),
            'column_types': infer_column_types(data)
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Error parsing JSON: {str(e)}'
        }


def infer_column_types(df):
    """
    Infer column data types
    Returns: {
        'column_name': 'type'
    }
    """
    column_types = {}
    
    for column in df.columns:
        dtype = str(df[column].dtype)
        
        if 'int' in dtype:
            column_types[column] = 'integer'
        elif 'float' in dtype:
            column_types[column] = 'float'
        elif 'object' in dtype:
            column_types[column] = 'string'
        elif 'datetime' in dtype:
            column_types[column] = 'datetime'
        elif 'bool' in dtype:
            column_types[column] = 'boolean'
        else:
            column_types[column] = 'mixed'
    
    return column_types

