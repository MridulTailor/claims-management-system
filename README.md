# ClaimsManager - Modern SaaS Claims Management System

A modern, responsive insurance claims management system built with Django and enhanced with Tailwind CSS + daisyUI for a professional SaaS-style user interface.

## 🚀 Features

### Modern UI/UX

- **Responsive Design**: Fully responsive across all device sizes using Tailwind CSS
- **daisyUI Components**: Pre-built, themeable, and accessible UI components
- **Multiple Themes**: Support for 27+ daisyUI themes (light, dark, corporate, etc.)
- **Interactive Elements**: Smooth animations and transitions
- **Toast Notifications**: Modern notification system
- **Loading States**: Professional skeleton loaders and progress indicators

### Claims Management

- **Advanced Filtering**: Search by patient name, claim ID, status, and insurer
- **Real-time Updates**: HTMX-powered dynamic content loading
- **Flag System**: Mark claims for review with custom reasons
- **Note System**: Add and manage claim annotations
- **Admin Dashboard**: Comprehensive analytics and metrics
- **Export Functionality**: Ready for data export features

### Technical Features

- **Performance Optimized**: Tailwind CSS purging for minimal bundle size
- **Accessibility**: WCAG compliant components via daisyUI
- **Alpine.js Integration**: Lightweight JavaScript for interactivity
- **Hot Reloading**: Development server with auto-refresh
- **Modern CSS**: Custom animations and hover effects
- **Clean Codebase**: Removed legacy templates and unnecessary files

## 🛠️ Technology Stack

- **Backend**: Django 5.2+
- **Frontend**: Tailwind CSS 4+ with daisyUI 5+
- **JavaScript**: Alpine.js 3+ and HTMX 1.9+
- **Icons**: Font Awesome 6+
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Package Management**: Pipenv

## 🏃‍♂️ Quick Start

### Prerequisites

- Python 3.13+
- Node.js 18+
- Pipenv

### Development Setup

1. **Clone and enter the project**:

   ```bash
   cd /path/to/claimsmanager
   ```

2. **Install dependencies**:

   ```bash
   pipenv install
   ```

3. **Run migrations**:

   ```bash
   pipenv run python manage.py migrate
   ```

4. **Load sample data** (if available):

   ```bash
   pipenv run python manage.py load_claims_data
   ```

5. **Start development servers**:

   ```bash
   # Option 1: Use the helper script (recommended)
   ./dev.sh start

   # Option 2: Manual startup
   # Terminal 1: Start Tailwind CSS watcher
   pipenv run python manage.py tailwind start

   # Terminal 2: Start Django server
   pipenv run python manage.py runserver
   ```

6. **Access the application**:
   - Main application: http://localhost:8000
   - Admin panel: http://localhost:8000/admin

## 🎨 UI Themes

The application supports multiple themes that can be switched dynamically:

- **Light** (default): Clean, professional light theme
- **Dark**: Modern dark theme for low-light environments
- **Corporate**: Business-focused professional theme
- **Cupcake**: Soft, pastel theme
- And 20+ more themes available through the theme switcher

Themes persist across sessions and are stored in localStorage.

## 📱 Responsive Design

The interface is fully responsive with breakpoints:

- **Mobile**: < 768px - Optimized touch interface
- **Tablet**: 768px - 1024px - Balanced layout
- **Desktop**: > 1024px - Full feature layout
- **Wide**: > 1280px - Enhanced spacing and content

## 🏗️ Project Structure

```
claimsmanager/
├── claims/                     # Main Django app
│   ├── templates/
│   │   ├── claims/
│   │   │   ├── base_modern.html           # Modern base template
│   │   │   ├── claims_list_modern.html    # Main dashboard
│   │   │   ├── admin_dashboard_modern.html # Analytics
│   │   │   └── ...
│   │   ├── components/         # Reusable components
│   │   └── registration/       # Authentication templates
│   ├── templatetags/          # Custom template filters
│   └── ...
├── theme/                     # Tailwind CSS app
│   ├── static_src/
│   │   ├── src/styles.css    # Main stylesheet
│   │   └── package.json      # Node.js dependencies
│   └── static/               # Built CSS files
├── claims_management/        # Django project settings
├── data/                    # Sample data files
└── manage.py
```

## 🔜 Future Enhancements

- [ ] Advanced data visualization charts
- [ ] Real-time notifications via WebSockets
- [ ] API endpoints for mobile app integration
- [ ] Advanced reporting and export features
- [ ] Multi-tenant support
- [ ] Integration with external insurance APIs

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for complete details.

---
