# Real Estate AI Chatbot - API Documentation

## Overview
This document provides comprehensive API documentation for the Real Estate AI Chatbot application, including endpoints, request/response formats, error handling, and integration examples.

## Base URL
- **Development**: `http://localhost:5000`
- **Production**: `https://your-app-domain.com`

## Authentication
Currently, the API does not require authentication. Future versions may implement API key authentication.

## Content Type
All API requests should use `Content-Type: application/json` for POST requests.

---

## API Endpoints

### 1. Natural Language Search

#### **POST** `/api/nl_search`

**Description**: Process natural language queries and return property listings or AI-generated responses.

**Request Body**:
```json
{
  "query": "string"
}
```

**Request Example**:
```json
{
  "query": "all current villa for sale in Damac hills"
}
```

**Response Format**:

**Success Response (Property Listings)**:
```json
[
  {
    "id": "15316766",
    "title": "Vacant | Golf Course and Pool View | High ROI",
    "price": 1200000,
    "area": 743,
    "rooms": 1,
    "baths": 1,
    "purpose": "Residential for Sale",
    "completion_status": "completed",
    "latitude": 25.0141658782959,
    "longitude": 55.25063705444336,
    "location_name": "Golf Promenade 3B, Golf Promenade, DAMAC Hills, Dubai",
    "cover_photo_url": "https://www.propertyfinder.ae/property/...",
    "all_image_urls": "https://www.propertyfinder.ae/property/...",
    "agency_name": "ALH PROPERTIES",
    "contact_name": "Ken Michael Gelera",
    "mobile_number": "+971565202365",
    "whatsapp_number": "+97145560345",
    "down_payment_percentage": null
  }
]
```

**Success Response (Question Answer)**:
```json
{
  "is_question": true,
  "question_type": "price_range",
  "filters": {
    "property_type": "villa",
    "query": "Dubai Marina"
  },
  "answer": {
    "min_price": 1500000,
    "max_price": 8500000,
    "text": "The price range for villas in Dubai Marina is AED 1,500,000 – AED 8,500,000"
  },
  "data": [...]
}
```

**Error Response**:
```json
{
  "error": "Invalid query format",
  "message": "Please provide a valid search query"
}
```

**Status Codes**:
- `200 OK`: Successful request
- `400 Bad Request`: Invalid request format
- `500 Internal Server Error`: Server error

---

### 2. Structured Property Search

#### **GET** `/api/search`

**Description**: Search properties using structured parameters.

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `purpose` | string | No | Property purpose ("for-sale", "for-rent") |
| `rooms` | integer | No | Number of bedrooms |
| `baths` | integer | No | Number of bathrooms |
| `min_price` | integer | No | Minimum price filter |
| `max_price` | integer | No | Maximum price filter |
| `page` | integer | No | Page number (default: 1) |
| `limit` | integer | No | Results per page (default: 10) |

**Request Example**:
```
GET /api/search?purpose=for-sale&rooms=3&min_price=1000000&max_price=5000000
```

**Response Format**:
```json
{
  "properties": [...],
  "page": 1,
  "limit": 10,
  "total_properties": 25,
  "total_pages": 3
}
```

---

### 3. Property Details

#### **GET** `/api/properties/{property_id}`

**Description**: Get detailed information for a specific property.

**Path Parameters**:
- `property_id` (string): Unique property identifier

**Request Example**:
```
GET /api/properties/15316766
```

**Response Format**:
```json
{
  "id": "15316766",
  "title": "Vacant | Golf Course and Pool View | High ROI",
  "price": 1200000,
  "area": 743,
  "rooms": 1,
  "baths": 1,
  "purpose": "Residential for Sale",
  "completion_status": "completed",
  "latitude": 25.0141658782959,
  "longitude": 55.25063705444336,
  "location_name": "Golf Promenade 3B, Golf Promenade, DAMAC Hills, Dubai",
  "cover_photo_url": "https://www.propertyfinder.ae/property/...",
  "all_image_urls": ["https://www.propertyfinder.ae/property/..."],
  "agency_name": "ALH PROPERTIES",
  "contact_name": "Ken Michael Gelera",
  "mobile_number": "+971565202365",
  "whatsapp_number": "+97145560345",
  "down_payment_percentage": null
}
```

**Error Response**:
```json
{
  "error": "Property not found",
  "message": "Property with ID 15316766 not found in cache"
}
```

---

### 4. Image Proxy

#### **GET** `/get_image`

**Description**: Proxy service for property images to handle CORS issues.

**Query Parameters**:
- `url` (string, required): URL of the image to retrieve

**Request Example**:
```
GET /get_image?url=https%3A%2F%2Fwww.propertyfinder.ae%2Fproperty%2F...
```

**Response**: Binary image data with appropriate content-type headers.

**Error Responses**:
- `400 Bad Request`: Invalid image URL
- `404 Not Found`: Image not found
- `408 Request Timeout`: Image fetch timed out
- `500 Internal Server Error`: Server error

---

### 5. Map View

#### **GET** `/map_view`

**Description**: Render a map view for property location.

**Query Parameters**:
- `lat` (float, required): Latitude coordinate
- `lng` (float, required): Longitude coordinate

**Request Example**:
```
GET /map_view?lat=25.0141658782959&lng=55.25063705444336
```

**Response**: HTML page with interactive map showing property location.

---

## Data Models

### Property Object
```json
{
  "id": "string",
  "title": "string",
  "price": "number",
  "area": "number",
  "rooms": "integer",
  "baths": "integer",
  "purpose": "string",
  "completion_status": "string",
  "latitude": "number",
  "longitude": "number",
  "location_name": "string",
  "cover_photo_url": "string",
  "all_image_urls": "string|array",
  "agency_name": "string",
  "contact_name": "string",
  "mobile_number": "string",
  "whatsapp_number": "string",
  "down_payment_percentage": "number|null"
}
```

### Question Response Object
```json
{
  "is_question": "boolean",
  "question_type": "string",
  "filters": "object",
  "answer": "object",
  "data": "array"
}
```

---

## Error Handling

### Standard Error Response Format
```json
{
  "error": "Error Type",
  "message": "Human-readable error message",
  "code": "ERROR_CODE",
  "details": "Additional error details (optional)"
}
```

### Common Error Codes
| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_QUERY` | 400 | Invalid query format |
| `PROPERTY_NOT_FOUND` | 404 | Property not found |
| `API_ERROR` | 502 | External API error |
| `TIMEOUT` | 408 | Request timeout |
| `SERVER_ERROR` | 500 | Internal server error |

---

## Rate Limiting

Currently, no rate limiting is implemented. Future versions may include:
- 100 requests per minute per IP
- 1000 requests per hour per IP
- Burst allowance for legitimate usage

---

## Caching

### Cache Strategy
- **TTL**: 30 minutes for all cached queries
- **Cache Key**: Based on query parameters
- **Storage**: SQLite database
- **Invalidation**: Automatic expiration

### Cache Headers
```http
Cache-Control: public, max-age=1800
ETag: "query-hash"
Last-Modified: "timestamp"
```

---

## Integration Examples

### JavaScript/Frontend Integration
```javascript
// Natural language search
async function searchProperties(query) {
  const response = await fetch('/api/nl_search', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ query: query })
  });
  
  if (response.ok) {
    const data = await response.json();
    return data;
  } else {
    throw new Error('Search failed');
  }
}

// Usage
searchProperties('villas for sale in Dubai Marina')
  .then(properties => {
    console.log('Found properties:', properties);
    // Display properties in UI
  })
  .catch(error => {
    console.error('Search error:', error);
  });
```

### Python Integration
```python
import requests

def search_properties(query):
    url = 'http://localhost:5000/api/nl_search'
    payload = {'query': query}
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f'Error: {e}')
        return None

# Usage
properties = search_properties('apartments for rent in Downtown Dubai')
if properties:
    for prop in properties:
        print(f"{prop['title']} - AED {prop['price']:,}")
```

### cURL Examples
```bash
# Natural language search
curl -X POST -H "Content-Type: application/json" \
  -d '{"query": "villas for sale in Damac hills"}' \
  http://localhost:5000/api/nl_search

# Structured search
curl "http://localhost:5000/api/search?purpose=for-sale&rooms=3&min_price=1000000"

# Property details
curl "http://localhost:5000/api/properties/15316766"

# Image proxy
curl "http://localhost:5000/get_image?url=https%3A%2F%2Fwww.propertyfinder.ae%2Fproperty%2F..."
```

---

## Testing

### Test Endpoints
```bash
# Health check
curl http://localhost:5000/

# Test natural language processing
curl -X POST -H "Content-Type: application/json" \
  -d '{"query": "test query"}' \
  http://localhost:5000/api/nl_search
```

### Load Testing
```bash
# Using Apache Bench
ab -n 100 -c 10 -H "Content-Type: application/json" \
  -p test_query.json http://localhost:5000/api/nl_search
```

---

## Future Enhancements

### Planned Features
1. **Authentication**: API key-based authentication
2. **Rate Limiting**: Request throttling and quotas
3. **Webhooks**: Real-time property updates
4. **GraphQL**: Alternative query interface
5. **Bulk Operations**: Batch property processing
6. **Analytics**: Usage tracking and metrics

### API Versioning
- Current version: v1
- Future versions will use URL versioning: `/api/v2/...`
- Backward compatibility maintained for at least 6 months

---

## Support

For API support and questions:
- **Documentation**: This document and inline code comments
- **Issues**: GitHub issues for bug reports
- **Development**: Local development setup guide

---

## Changelog

### Version 1.0.0
- Initial API release
- Natural language search endpoint
- Property search and details endpoints
- Image proxy service
- Map integration
- Caching system implementation
