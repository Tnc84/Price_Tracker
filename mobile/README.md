# 📱 Romanian Price Tracker - Android App

Kotlin Android app for tracking product prices across Romanian retailers.

## Features

- 🔍 Search products across retailers
- 💰 Compare prices in real-time
- 📊 View price history and trends
- 🔔 Price drop notifications
- 🏪 Browse deals from all retailers
- 📱 Modern Material Design UI

## Tech Stack

- **Language**: Kotlin
- **UI**: Jetpack Compose
- **Architecture**: MVVM + Repository pattern
- **Networking**: Retrofit + OkHttp
- **Async**: Coroutines + Flow
- **Dependency Injection**: Hilt
- **Image Loading**: Coil

## Setup

### Prerequisites

- Android Studio Hedgehog or newer
- Android SDK 24+ (Android 7.0+)
- JDK 11+

### Build & Run

1. Open project in Android Studio
2. Sync Gradle files
3. Update API URL in `build.gradle.kts`:
   ```kotlin
   buildConfigField("String", "API_BASE_URL", "\"http://10.0.2.2:8000/api/v1/\"")
   ```
4. Run on emulator or device

### Configuration

Edit `local.properties`:
```properties
api.base.url=http://10.0.2.2:8000/api/v1/
```

## Project Structure

```
app/
├── src/main/
│   ├── java/com/ro/pricetracker/
│   │   ├── MainActivity.kt
│   │   ├── models/           # Data models
│   │   ├── network/          # API service
│   │   ├── repository/       # Data repositories
│   │   ├── viewmodel/        # ViewModels
│   │   ├── ui/              # Compose UI
│   │   │   ├── screens/
│   │   │   ├── components/
│   │   │   └── theme/
│   │   └── utils/           # Utilities
│   └── res/                 # Resources
└── build.gradle.kts
```

## Screens

### Home Screen
- Product list with current prices
- Search functionality
- Filter by category/retailer

### Product Details
- Price comparison chart
- Price history graph
- Retailer links
- Set price alerts

### Add Product
- Search form
- Category selection
- Target price input

### Deals Screen
- Current promotions
- Best deals
- Filter by discount %

## API Integration

The app connects to the FastAPI backend:

```kotlin
interface ApiService {
    @GET("products/")
    suspend fun getProducts(): List<Product>
    
    @GET("products/{id}")
    suspend fun getProduct(@Path("id") id: Int): ProductWithPrices
    
    @POST("products/")
    suspend fun createProduct(@Body product: ProductCreate): Product
    
    @GET("prices/comparison/{id}")
    suspend fun getPriceComparison(@Path("id") id: Int): PriceComparison
    
    @POST("products/{id}/scrape")
    suspend fun scrapeProduct(@Path("id") id: Int): ScrapeResponse
}
```

## Building for Release

```bash
# Generate signed APK
./gradlew assembleRelease

# Generate AAB for Google Play
./gradlew bundleRelease
```

## Testing

```bash
# Run unit tests
./gradlew test

# Run instrumented tests
./gradlew connectedAndroidTest
```

## License

MIT License

