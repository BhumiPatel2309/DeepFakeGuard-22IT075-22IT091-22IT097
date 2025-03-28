import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from src.auth.login import login_page

@pytest.fixture
def mock_streamlit():
    """Create a mock Streamlit instance with all required components"""
    with patch('src.auth.login.st') as mock_st:
        # Mock session state as a property
        mock_session_state = {}
        type(mock_st).session_state = PropertyMock(return_value=mock_session_state)
        
        # Mock form and form components
        mock_form = MagicMock()
        mock_form.text_input = MagicMock(return_value="")  # Default empty value
        mock_form.form_submit_button = MagicMock(return_value=True)  # Form is submitted by default
        mock_st.form.return_value.__enter__.return_value = mock_form
        mock_st.form.return_value.__exit__.return_value = None
        
        # Mock columns
        mock_col = MagicMock()
        mock_st.columns.return_value = [mock_col, mock_col, mock_col]
        
        # Mock query params
        mock_st.experimental_get_query_params = MagicMock(return_value={})
        mock_st.experimental_set_query_params = MagicMock()
        
        # Mock other Streamlit components
        mock_st.button = MagicMock(return_value=False)
        mock_st.markdown = MagicMock()
        mock_st.success = MagicMock()
        mock_st.error = MagicMock()
        
        yield mock_st

class TestLoginPage:
    @patch('src.auth.login.is_valid_username')
    @patch('src.auth.login.login_user')
    def test_login_form_validation(self, mock_login, mock_validate, mock_streamlit):
        # Test empty form submission
        mock_form = mock_streamlit.form.return_value.__enter__.return_value
        mock_form.text_input.return_value = ""
        
        login_page()
        mock_streamlit.error.assert_called_with("Please fill in all fields")

        # Test invalid username
        mock_form.text_input.side_effect = ["123user", "password"]
        mock_validate.return_value = False
        
        login_page()
        mock_streamlit.error.assert_called_with("Invalid username format. Please check your username.")

    @patch('src.auth.login.login_user')
    def test_successful_login(self, mock_login, mock_streamlit):
        # Mock successful login response
        mock_login.return_value = (
            True,
            "Login successful",
            {
                "username": "testuser",
                "email": "test@example.com",
                "phone": "+1234567890",
                "is_admin": False
            }
        )

        # Set up form inputs for successful login
        mock_form = mock_streamlit.form.return_value.__enter__.return_value
        mock_form.text_input.side_effect = ["testuser", "TestPass123!"]

        # Test login
        login_page()

        # Verify session state is updated
        assert mock_streamlit.session_state["logged_in"] == True
        assert mock_streamlit.session_state["username"] == "testuser"
        assert mock_streamlit.session_state["email"] == "test@example.com"
        mock_streamlit.success.assert_called_with("Login successful")

    @patch('src.auth.login.get_google_auth_url')
    def test_google_signin_button(self, mock_get_auth_url, mock_streamlit):
        # Mock Google auth URL
        auth_url = "https://accounts.google.com/o/oauth2/auth?..."
        mock_get_auth_url.return_value = auth_url
        
        # Mock button click for Google sign-in
        mock_streamlit.button.return_value = True
        
        # Test Google sign-in button
        login_page()
        
        # Verify auth URL is generated and redirect is attempted
        mock_get_auth_url.assert_called_once()
        mock_streamlit.markdown.assert_called_with(
            f'<meta http-equiv="refresh" content="0;url={auth_url}">',
            unsafe_allow_html=True
        )

    @patch('src.auth.login.handle_oauth_callback')
    def test_oauth_callback_handling(self, mock_handler, mock_streamlit):
        # Mock query parameters for OAuth callback
        mock_streamlit.experimental_get_query_params.return_value = {
            "code": ["test_auth_code"],
            "state": ["test_state"]
        }

        # Mock form inputs to prevent validation errors
        mock_form = mock_streamlit.form.return_value.__enter__.return_value
        mock_form.text_input.return_value = "testuser"  # Return valid username for validation
        mock_form.form_submit_button.return_value = False  # Don't submit form during OAuth

        # Test successful callback
        mock_handler.return_value = (True, "Successfully authenticated with Google")
        login_page()
        mock_streamlit.success.assert_called_with("Successfully authenticated with Google")
        mock_streamlit.experimental_set_query_params.assert_called()

        # Reset mocks
        mock_streamlit.reset_mock()
        mock_handler.reset_mock()

        # Test failed callback
        mock_handler.return_value = (False, "Authentication failed")
        login_page()
        mock_streamlit.error.assert_called_with("Authentication failed")
        mock_streamlit.experimental_set_query_params.assert_called()
