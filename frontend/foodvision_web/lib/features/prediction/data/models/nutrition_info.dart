class NutritionInfo {
  final int calories;
  final double protein;
  final double carbs;
  final double fat;
  final List<String> tags;

  const NutritionInfo({
    required this.calories,
    required this.protein,
    required this.carbs,
    required this.fat,
    required this.tags,
  });

  /// Intelligent heuristics mapping food names from the 270 classes to estimated macros per 100g.
  factory NutritionInfo.forFood(String foodName) {
    final name = foodName.toLowerCase().replaceAll('_', ' ');

    // Salads & Raw Vegetables
    if (name.contains('salad') || name.contains('spinach') || name.contains('carrot') || name.contains('artichoke')) {
      return const NutritionInfo(
        calories: 85,
        protein: 2.5,
        carbs: 8.0,
        fat: 4.5,
        tags: ['Vegetarian', 'Vegan', 'Low-Calorie', 'High-Fiber'],
      );
    }

    // Soups & Broths
    if (name.contains('soup') || name.contains('noodle') || name.contains('ramen')) {
      return const NutritionInfo(
        calories: 145,
        protein: 7.0,
        carbs: 18.0,
        fat: 4.0,
        tags: ['Comfort Food', 'Warm Serving'],
      );
    }

    // High-Protein Meats, Steaks & Kebabs
    if (name.contains('wagyu') || name.contains('kebab') || name.contains('rib') || name.contains('steak') || name.contains('chicken') || name.contains('beef')) {
      return const NutritionInfo(
        calories: 265,
        protein: 26.0,
        carbs: 2.0,
        fat: 17.0,
        tags: ['High-Protein', 'Keto-Friendly'],
      );
    }

    // Seafood, Clams & Fish
    if (name.contains('clam') || name.contains('fish') || name.contains('tobiko') || name.contains('salmon') || name.contains('shrimp')) {
      return const NutritionInfo(
        calories: 130,
        protein: 21.0,
        carbs: 1.5,
        fat: 3.5,
        tags: ['High-Protein', 'Pescatarian', 'Omega-3'],
      );
    }

    // Desserts, Pastries, Cakes & Baklava
    if (name.contains('cake') || name.contains('pastry') || name.contains('pancake') || name.contains('baklava') || name.contains('pie') || name.contains('dessert') || name.contains('churros')) {
      return const NutritionInfo(
        calories: 380,
        protein: 5.5,
        carbs: 52.0,
        fat: 18.5,
        tags: ['Sweet', 'Energy-Dense', 'Vegetarian'],
      );
    }

    // Pizza, Burgers & Sandwiches
    if (name.contains('pizza') || name.contains('burger') || name.contains('sandwich')) {
      return const NutritionInfo(
        calories: 275,
        protein: 12.0,
        carbs: 31.0,
        fat: 11.5,
        tags: ['Fast Casual', 'Savory'],
      );
    }

    // Default Balanced Food Baseline
    return const NutritionInfo(
      calories: 210,
      protein: 10.0,
      carbs: 24.0,
      fat: 8.0,
      tags: ['Balanced Meal'],
    );
  }
}