import pytest
import json
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path to import main
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app

@pytest.fixture
def client():
    """Create a test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_table():
    """Mock DynamoDB table"""
    with patch('main.table') as mock:
        yield mock

class TestHealthCheck:
    """Test health check endpoint"""
    
    def test_health_check(self, client):
        """Test health endpoint returns 200 and correct status"""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'OK'

class TestListTodos:
    """Test listing todos"""
    
    def test_get_todos_empty(self, client, mock_table):
        """Test getting todos when table is empty"""
        mock_table.scan.return_value = {'Items': []}
        
        response = client.get('/api/todos')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data == []
    
    def test_get_todos_with_items(self, client, mock_table):
        """Test getting todos with items"""
        mock_items = [
            {'id': '1', 'title': 'Test Task 1', 'done': False},
            {'id': '2', 'title': 'Test Task 2', 'done': True}
        ]
        mock_table.scan.return_value = {'Items': mock_items}
        
        response = client.get('/api/todos')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 2
        assert data[0]['title'] == 'Test Task 1'
        assert data[1]['done'] is True
    
    def test_get_todos_error_handling(self, client, mock_table):
        """Test error handling when scan fails"""
        mock_table.scan.side_effect = Exception('DynamoDB error')
        
        response = client.get('/api/todos')
        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'error' in data

class TestCreateTodo:
    """Test creating todos"""
    
    def test_create_todo_success(self, client, mock_table):
        """Test creating a new todo"""
        mock_table.put_item.return_value = {}
        
        response = client.post('/api/todos', 
                              json={'title': 'New Task'},
                              content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['title'] == 'New Task'
        assert data['done'] is False
        assert 'id' in data
        
        # Verify put_item was called
        mock_table.put_item.assert_called_once()
    
    def test_create_todo_with_empty_title(self, client, mock_table):
        """Test creating todo with empty title"""
        mock_table.put_item.return_value = {}
        
        response = client.post('/api/todos', 
                              json={'title': ''},
                              content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['title'] == ''
    
    def test_create_todo_error_handling(self, client, mock_table):
        """Test error handling when put_item fails"""
        mock_table.put_item.side_effect = Exception('DynamoDB error')
        
        response = client.post('/api/todos',
                              json={'title': 'New Task'},
                              content_type='application/json')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'error' in data

class TestUpdateTodo:
    """Test updating todos"""
    
    def test_update_todo_success(self, client, mock_table):
        """Test updating a todo"""
        mock_table.update_item.return_value = {}
        
        response = client.put('/api/todos/1',
                             json={'title': 'Updated Task', 'done': True},
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'updated'
        
        # Verify update_item was called with correct parameters
        mock_table.update_item.assert_called_once()
        call_kwargs = mock_table.update_item.call_args[1]
        assert call_kwargs['Key'] == {'id': '1'}
        assert call_kwargs['ExpressionAttributeValues'][':title'] == 'Updated Task'
        assert call_kwargs['ExpressionAttributeValues'][':done'] is True
    
    def test_update_todo_partial(self, client, mock_table):
        """Test updating only title"""
        mock_table.update_item.return_value = {}
        
        response = client.put('/api/todos/1',
                             json={'title': 'Only Title', 'done': False},
                             content_type='application/json')
        
        assert response.status_code == 200
    
    def test_update_todo_error_handling(self, client, mock_table):
        """Test error handling when update fails"""
        mock_table.update_item.side_effect = Exception('DynamoDB error')
        
        response = client.put('/api/todos/1',
                             json={'title': 'Updated Task', 'done': True},
                             content_type='application/json')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'error' in data

class TestDeleteTodo:
    """Test deleting todos"""
    
    def test_delete_todo_success(self, client, mock_table):
        """Test deleting a todo"""
        mock_table.delete_item.return_value = {}
        
        response = client.delete('/api/todos/1')
        assert response.status_code == 204
        
        # Verify delete_item was called with correct key
        mock_table.delete_item.assert_called_once()
        call_kwargs = mock_table.delete_item.call_args[1]
        assert call_kwargs['Key'] == {'id': '1'}
    
    def test_delete_todo_error_handling(self, client, mock_table):
        """Test error handling when delete fails"""
        mock_table.delete_item.side_effect = Exception('DynamoDB error')
        
        response = client.delete('/api/todos/1')
        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'error' in data

class TestCORS:
    """Test CORS headers"""
    
    def test_cors_headers_present(self, client):
        """Test CORS headers are present on GET request"""
        response = client.get('/api/todos')
        assert 'Access-Control-Allow-Origin' in response.headers
    
    def test_cors_headers_on_post(self, client, mock_table):
        """Test CORS headers are present on POST request"""
        mock_table.put_item.return_value = {}
        
        response = client.post('/api/todos',
                              json={'title': 'Test'},
                              content_type='application/json')
        assert 'Access-Control-Allow-Origin' in response.headers
