# SEVASETU MVP Development Tasks

## 🎯 Priority Tasks for Admin Portal & Citizen Portal Integration

### **Phase 1: Core Functionality (Week 2 Focus)**

#### 📍 Location & Map Improvements
- [ ] **Citizen Portal Location Fix**
  - [ ] Replace lat/lon input fields with interactive map
  - [ ] Implement functional "Use My Location" button with geolocation API
  - [ ] Add map click to set report location
  - [ ] Handle geolocation permissions and errors
  - [ ] Add location accuracy indicator

#### 🏢 Departments Management (Admin Portal)
- [ ] **Backend API Development**
  - [ ] Add Department models (name, email, created_at, updated_at)
  - [ ] Create CRUD endpoints: GET, POST, PUT, DELETE /api/departments
  - [ ] Implement alphabetical sorting
  - [ ] Add search functionality
  - [ ] Handle soft delete (preserve report history)

- [ ] **Frontend Implementation**
  - [ ] Complete Departments page (replace placeholder)
  - [ ] Add department CRUD operations UI
  - [ ] Implement data table with search/pagination
  - [ ] Add create/edit forms with validation
  - [ ] Add delete confirmation dialogs

#### 🔍 Enhanced Reports Filtering (Admin Portal)
- [ ] **Location-Based Filtering**
  - [ ] Add location parameters to reports API (center_lat, center_lng, radius_km)
  - [ ] Implement geolocation hook for admin location
  - [ ] Add radius selector (1km, 2km, 5km, 10km, 25km, 50km, All)
  - [ ] Default: 10km radius from user location
  - [ ] Add "Use My Location" and map click center selection

- [ ] **Additional Filters**
  - [ ] Date range picker (from/to dates)
  - [ ] Department dropdown (from departments table)
  - [ ] Enhanced category filtering
  - [ ] Status filtering (existing)
  - [ ] Combined AND logic for all filters

#### 🗺️ Map View Enhancements
- [ ] **Reports Map Priority**
  - [ ] Make map view the default/primary view
  - [ ] Add filter visualization (radius circle overlay)
  - [ ] Implement map-based location selection
  - [ ] Add report clustering for better performance
  - [ ] Show filtered results on map

### **Phase 2: Polish & Integration (Week 3-4 Focus)**

#### 🎨 Branding Updates (SEVASETU)
- [ ] Update all references from CityPulse to SEVASETU
- [ ] Update login page branding
- [ ] Update headers and navigation
- [ ] Update page titles and meta information

#### 🚀 Performance & UX
- [ ] Add loading states and skeleton screens
- [ ] Implement error boundaries and fallback UIs
- [ ] Add proper error handling for geolocation
- [ ] Optimize API queries with caching
- [ ] Add pagination for large datasets

#### 📱 Mobile Responsiveness
- [ ] Test and fix mobile geolocation
- [ ] Optimize map interactions for touch
- [ ] Ensure forms work well on mobile
- [ ] Test filter UI on small screens

## 🔧 Technical Implementation Details

### **Database Schema (Existing)**
```sql
-- departments table (existing)
id, name, email, created_at, updated_at

-- category_department_mapping (existing)  
category_name, department_id

-- reports table (existing)
id, description, latitude, longitude, category, status, user_id, department_id, created_at
```

### **API Endpoints to Implement**
```
# Departments
GET /api/departments - List departments (alphabetical)
POST /api/departments - Create department  
PUT /api/departments/{id} - Update department
DELETE /api/departments/{id} - Soft delete

# Enhanced Reports  
GET /api/reports/all?status&category&department_id&date_from&date_to&center_lat&center_lng&radius_km
```

### **Frontend Components to Build**
- `DepartmentsPage.tsx` - Full CRUD interface
- `LocationFilter.tsx` - Geographic filtering component  
- `GeolocationHook.tsx` - User location management
- `InteractiveMap.tsx` - Map with click selection (Citizen Portal)
- `ReportsMapView.tsx` - Enhanced map view with filters

## ⚡ Immediate Next Steps

1. **Start with Citizen Portal location fixes** (impacts user experience)
2. **Implement Departments backend API** (foundational)
3. **Build Departments frontend** (admin functionality)
4. **Add location filtering to Reports** (enhanced admin tools)
5. **Polish and test** (MVP readiness)

## 🎯 Success Criteria

- [ ] Citizen can select location by clicking map or using "Use My Location"
- [ ] Admin can manage departments (create, edit, delete, view)
- [ ] Admin can filter reports by location within customizable radius
- [ ] All filters work together (date, category, status, department, location)
- [ ] Map view is prioritized and functional
- [ ] Mobile experience is responsive and functional
- [ ] SEVASETU branding is consistently applied