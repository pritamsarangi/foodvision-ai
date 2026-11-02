import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:foodvision_web/features/prediction/cubit/image_picker_cubit.dart';

import 'core/theme/app_theme.dart';
import 'features/prediction/presentation/prediction_screen.dart';

import 'core/network/api_client.dart';
import 'features/prediction/cubit/prediction_cubit.dart';
import 'features/prediction/data/repositories/prediction_repository.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const FoodVisionApp());
}

class FoodVisionApp extends StatelessWidget {
  const FoodVisionApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'FoodVision AI',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      home: MultiBlocProvider(
        providers: [
          BlocProvider(create: (_) => ImagePickerCubit()),
          BlocProvider(
            create: (_) => PredictionCubit(PredictionRepository(ApiClient())),
          ),
        ],
        child: const PredictionScreen(),
      ),
    );
  }
}
