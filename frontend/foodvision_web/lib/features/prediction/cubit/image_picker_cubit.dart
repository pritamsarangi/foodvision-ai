
import 'dart:typed_data';

import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:image_picker/image_picker.dart';

class ImagePickerState {
  final Uint8List? imageBytes;
  final String? fileName;
  final String? error;

  const ImagePickerState({
    this.imageBytes,
    this.fileName,
    this.error,
  });
}

class ImagePickerCubit extends Cubit<ImagePickerState> {
  ImagePickerCubit() : super(const ImagePickerState());

  final ImagePicker _picker = ImagePicker();

  Future<void> pickImage() async {
    try {
      final file = await _picker.pickImage(
        source: ImageSource.gallery,
      );

      if (file == null) return;

      final bytes = await file.readAsBytes();

      if (bytes.isEmpty) {
        emit(const ImagePickerState(error: 'Image is empty'));
        return;
      }

      if (bytes.length > 10 * 1024 * 1024) {
        emit(const ImagePickerState(error: 'Image exceeds 10 MB'));
        return;
      }

      emit(ImagePickerState(
        imageBytes: bytes,
        fileName: file.name,
      ));
    } catch (_) {
      emit(const ImagePickerState(
        error: 'Unable to select image',
      ));
    }
  }

  void clearImage() {
    emit(const ImagePickerState());
  }
}
