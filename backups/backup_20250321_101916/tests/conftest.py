import pytest
import streamlit as st
from unittest.mock import MagicMock

@pytest.fixture
def mock_st():
    # Mock streamlit session state
    if not hasattr(st, "session_state"):
        st.session_state = {}
    return st

@pytest.fixture
def mock_logger():
    return MagicMock()

@pytest.fixture
def mock_database():
    return MagicMock()
