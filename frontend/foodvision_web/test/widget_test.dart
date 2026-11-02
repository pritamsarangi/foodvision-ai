
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:foodvision_web/main.dart';

void main() {
  testWidgets('FoodVision landing screen loads', (tester) async {
    await tester.pumpWidget(const FoodVisionApp());

    expect(find.text('FoodVision AI'), findsOneWidget);
    expect(find.text('Discover Your Food with AI'), findsOneWidget);
    expect(
      find.byIcon(Icons.cloud_upload_outlined),
      findsOneWidget,
    );
  });
}
