# FGN Savings Bond Application - Web Migration and Deployment Specification

## Overview
This document outlines the plan to deprecate the desktop GUI portion of the FGN Savings Bond application and enhance the web-based Streamlit application for production deployment. The goal is to create a robust, accessible, and easily deployable application that can be hosted on cloud or local servers.

## Current Architecture
The application currently has two interfaces:
1. **Desktop GUI** (PyQt6-based) - To be deprecated
2. **Web Interface** (Streamlit-based) - To be enhanced and prepared for production

## Current Issues to Address
1. **Database Inconsistency**: The codebase references both SQLite (in form_handler.py) and MongoDB (in streamlit_app.py)
2. **Admin Functionality Exposure**: The "View Submissions" tab is accessible to all users, which is a security concern
3. **Code Organization**: Need to separate user-facing and admin functionality

## Migration Plan

### Phase 1: Deprecate Desktop GUI
- Remove desktop GUI-related files
- Refactor shared components to focus on web implementation
- Ensure all functionality is preserved in the web version

### Phase 2: Standardize Database and Enhance Web Application
- Standardize on MongoDB for all database operations
- Remove SQLite code and dependencies
- Separate user and admin functionality
- Improve user experience and interface
- Add additional validation and error handling
- Ensure responsive design for various devices

### Phase 3: Prepare for Production Deployment
- Containerize the application with Docker
- Set up environment configuration
- Implement logging and monitoring
- Create deployment documentation

## Detailed Implementation

### Phase 1: Deprecate Desktop GUI

#### Files to Remove:
- `src/gui.py` - PyQt6-based GUI implementation
- `src/main.py` - Desktop application entry point
- `run.py` - Script to launch the desktop application

#### Files to Refactor:
- `src/form_handler.py` - Remove GUI-specific code and dependencies

#### Files to Keep:
- `src/streamlit_app.py` - Web application
- `run_streamlit.py` - Script to launch the Streamlit app

### Phase 2: Enhance Web Application

#### User Experience Improvements:
- Ensure all form fields have appropriate validation
- Add progress indicators for multi-step processes
- Improve error messaging and user feedback

#### Security Enhancements:
- Implement proper input sanitization
- Secure database connections
- Add rate limiting for form submissions

### Phase 3: Production Deployment

#### Docker Configuration:
- Create Dockerfile for containerization
- Set up docker-compose for local development
- Configure environment variables

#### Deployment Options:
- Document deployment to various cloud providers (AWS, Azure, GCP)
- Provide instructions for local server deployment
- Set up CI/CD pipeline recommendations

#### Monitoring and Maintenance:
- Implement logging
- Set up health checks
- Create backup and restore procedures

## Technical Requirements

### Dependencies
- Python 3.10+
- Streamlit
- MongoDB
- ReportLab (for PDF generation)
- Docker

### Environment Variables
- `MONGO_URI`: MongoDB connection string
- `DB_NAME`: Database name
- `COLLECTION_NAME`: Collection name for applications
- `SECRET_KEY`: For secure operations
- `ENVIRONMENT`: Development/Production indicator

## Implementation Timeline
1. Phase 1: 1-2 days
2. Phase 2: 2-3 days
3. Phase 3: 2-3 days

Total estimated time: 5-8 days

## Success Criteria
- Desktop GUI completely removed
- Web application fully functional with all features
- Docker container successfully running the application
- Deployment documentation complete
- Application accessible and usable on various devices
