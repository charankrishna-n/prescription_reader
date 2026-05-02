"""
RXASSIST AI - FRONTEND SETUP GUIDE
===================================

OVERVIEW
--------
Modern, professional healthcare UI for prescription analysis using React, Framer Motion, and Tailwind CSS.

FEATURES
--------
✓ Landing page with hero section
✓ Prescription upload with drag & drop
✓ Medicine detection and display
✓ Medicine details page
✓ Smart reminder system
✓ Multi-language support (English, Tamil, Hindi)
✓ Browser notifications
✓ Responsive design (mobile, tablet, desktop)
✓ Smooth animations and transitions
✓ Professional healthcare design

TECH STACK
----------
- React 18.2.0
- React Router DOM 6.14.0
- Framer Motion 10.16.0
- Lucide React Icons 0.263.0
- Vite 4.4.0
- Axios 1.4.0

INSTALLATION
------------

1. Navigate to frontend directory:
   cd frontend

2. Install dependencies:
   npm install

3. Create .env file:
   VITE_API_URL=http://localhost:8000

4. Start development server:
   npm run dev

5. Open browser:
   http://localhost:3000

PROJECT STRUCTURE
-----------------

frontend/
├── src/
│   ├── pages/
│   │   ├── LandingPage.jsx
│   │   ├── LandingPage.css
│   │   ├── Dashboard.jsx
│   │   ├── Dashboard.css
│   │   ├── MedicineDetails.jsx
│   │   └── MedicineDetails.css
│   ├── components/
│   │   ├── Navigation.jsx
│   │   ├── Navigation.css
│   │   ├── MedicineCard.jsx
│   │   ├── MedicineCard.css
│   │   ├── NotificationCenter.jsx
│   │   ├── NotificationCenter.css
│   │   ├── ReminderModal.jsx
│   │   └── ReminderModal.css
│   ├── App.jsx
│   ├── App.css
│   ├── main.jsx
│   └── index.css
├── index.html
├── vite.config.js
├── package.json
└── README.md

PAGES
-----

1. LANDING PAGE (/)
   - Hero section with tagline
   - Feature cards
   - Benefits section
   - Call-to-action

2. DASHBOARD (/dashboard)
   - Prescription upload (drag & drop)
   - Medicine list display
   - Medicine cards with details
   - Reminder setup

3. MEDICINE DETAILS (/medicine/:id)
   - Detailed medicine information
   - Usage instructions
   - Warnings and side effects
   - Back to dashboard button

COMPONENTS
----------

Navigation
- Sticky navbar with logo
- Language selector (EN, TA, HI)
- Navigation links

MedicineCard
- Medicine name and icon
- Quantity, timing, duration
- Set reminder button
- View details button
- Confidence score

NotificationCenter
- Toast notifications
- Success, error, info types
- Auto-dismiss after 5 seconds
- Manual close button

ReminderModal
- Time selection (Morning, Afternoon, Evening)
- Browser notification toggle
- Save/Cancel buttons

STYLING
-------

Color Palette:
- Primary: #2E7DFF (Medical Blue)
- Secondary: #00C896 (Soft Green)
- Background: #F8FAFC (Light Clean)
- Text: #1E293B (Dark)
- Text Light: #64748B (Gray)

Design Features:
- Glassmorphism effect
- Soft shadows
- Rounded corners (16px)
- Smooth animations
- Professional healthcare look

ANIMATIONS
----------

- Page transitions (fade)
- Card hover effects
- Button interactions
- Loading spinner
- Notification slide-in
- Modal animations

RESPONSIVE DESIGN
-----------------

Mobile (< 768px):
- Single column layout
- Optimized touch targets
- Simplified navigation
- Stacked cards

Tablet (768px - 1024px):
- 2-column grid
- Adjusted spacing
- Optimized images

Desktop (> 1024px):
- Full multi-column layout
- Maximum width container
- Optimal spacing

MULTI-LANGUAGE SUPPORT
----------------------

Supported Languages:
- English (en)
- Tamil (ta)
- Hindi (hi)

Translations included for:
- All page titles
- Button labels
- Form labels
- Error messages
- Descriptions

API INTEGRATION
---------------

Backend Endpoint:
POST /predict

Request:
- multipart/form-data
- file: prescription image

Response:
{
  "status": "success",
  "filename": "prescription.jpg",
  "medicines": [
    {
      "medicine": "Augmentin",
      "quantity": "625mg",
      "when_to_take": "1-0-1",
      "duration": "5 days",
      "dosage_code": "1-0-1",
      "meal_context": "after meals",
      "confidence": 0.95
    }
  ],
  "raw_text": "..."
}

BROWSER NOTIFICATIONS
---------------------

Permission Request:
- Requested when setting reminders
- User can allow/deny

Notification Format:
- Title: Medicine name
- Body: Time and dosage
- Icon: Medicine icon

DEVELOPMENT
-----------

Start dev server:
npm run dev

Build for production:
npm build

Preview production build:
npm run preview

DEPLOYMENT
----------

1. Build the project:
   npm run build

2. Output directory:
   frontend/dist/

3. Deploy to hosting:
   - Vercel
   - Netlify
   - GitHub Pages
   - AWS S3 + CloudFront
   - Docker container

Environment Variables:
VITE_API_URL=https://api.example.com

PERFORMANCE
-----------

- Code splitting with React Router
- Lazy loading of components
- Optimized images
- Minified CSS/JS
- Smooth 60fps animations

ACCESSIBILITY
--------------

- Semantic HTML
- ARIA labels
- Keyboard navigation
- Color contrast compliance
- Focus indicators

BROWSER SUPPORT
---------------

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers

TROUBLESHOOTING
---------------

Issue: API connection failed
Solution:
1. Check backend is running on port 8000
2. Verify VITE_API_URL in .env
3. Check CORS settings on backend

Issue: Notifications not working
Solution:
1. Check browser notification permission
2. Verify browser supports Web Notifications API
3. Check browser notification settings

Issue: Styles not loading
Solution:
1. Clear browser cache
2. Restart dev server
3. Check CSS file paths

FUTURE ENHANCEMENTS
-------------------

- Dark mode support
- Medicine search functionality
- Prescription history
- Export prescription as PDF
- Integration with health apps
- Real-time medicine availability
- Pharmacy locator
- Medicine price comparison
- User authentication
- Cloud sync

CONTRIBUTING
------------

1. Create feature branch
2. Make changes
3. Test thoroughly
4. Submit pull request

CODE STYLE
----------

- Use functional components
- Use React hooks
- Use Framer Motion for animations
- Follow naming conventions
- Add comments for complex logic
- Keep components small and reusable

TESTING
-------

Manual testing checklist:
- [ ] All pages load correctly
- [ ] Responsive on mobile/tablet/desktop
- [ ] Language switching works
- [ ] Upload functionality works
- [ ] Reminders can be set
- [ ] Notifications display correctly
- [ ] All links work
- [ ] No console errors

SUPPORT
-------

For issues or questions:
1. Check this README
2. Review component documentation
3. Check browser console for errors
4. Contact development team

LICENSE
-------

Proprietary - RxAssist AI

CHANGELOG
---------

v1.0.0 - Initial Release
- Landing page
- Dashboard with upload
- Medicine details
- Reminder system
- Multi-language support
- Responsive design
"""
