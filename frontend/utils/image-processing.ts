import * as ImageManipulator from 'expo-image-manipulator';
import { Platform } from 'react-native';

export interface ImageData {
  uri: string;
  width: number;
  height: number;
  type: string;
  size?: number;
}

/**
 * Compress and optimize an image for upload
 * @param imageUri - URI of the image to compress
 * @param maxWidth - Maximum width (default 1200)
 * @param maxHeight - Maximum height (default 1200)
 * @param quality - JPEG quality 0-1 (default 0.8)
 * @returns Compressed image data
 */
export const compressImage = async (
  imageUri: string,
  maxWidth: number = 1200,
  maxHeight: number = 1200,
  quality: number = 0.8
): Promise<ImageData> => {
  try {
    const result = await ImageManipulator.manipulateAsync(imageUri, [], {
      compress: quality,
      format: ImageManipulator.SaveFormat.JPEG,
    });

    // Get image dimensions
    let width = result.width;
    let height = result.height;

    // Scale down if necessary
    if (width > maxWidth || height > maxHeight) {
      const aspectRatio = width / height;
      if (width > height) {
        width = maxWidth;
        height = Math.round(maxWidth / aspectRatio);
      } else {
        height = maxHeight;
        width = Math.round(maxHeight * aspectRatio);
      }

      const scaledResult = await ImageManipulator.manipulateAsync(
        result.uri,
        [{ resize: { width, height } }],
        { compress: quality, format: ImageManipulator.SaveFormat.JPEG }
      );

      return {
        uri: scaledResult.uri,
        width: scaledResult.width,
        height: scaledResult.height,
        type: 'image/jpeg',
      };
    }

    return {
      uri: result.uri,
      width: result.width,
      height: result.height,
      type: 'image/jpeg',
    };
  } catch (error) {
    throw new Error(
      `Image compression failed: ${error instanceof Error ? error.message : 'Unknown error'}`
    );
  }
};

/**
 * Correct image orientation based on EXIF data
 * Handles different device orientations
 * @param imageUri - URI of the image to correct
 * @returns Image data with corrected orientation
 */
export const correctImageOrientation = async (
  imageUri: string
): Promise<ImageData> => {
  try {
    // On Android, we may need to rotate based on device orientation
    // On iOS, expo-camera usually handles this automatically
    let rotation = 0;

    if (Platform.OS === 'android') {
      // Default rotation for Android camera output
      rotation = 90;
    }

    const result = await ImageManipulator.manipulateAsync(imageUri, [
      { rotate: rotation },
    ]);

    return {
      uri: result.uri,
      width: result.width,
      height: result.height,
      type: 'image/jpeg',
    };
  } catch (error) {
    throw new Error(
      `Image orientation correction failed: ${error instanceof Error ? error.message : 'Unknown error'}`
    );
  }
};

/**
 * Process image for upload - compress and correct orientation
 * @param imageUri - URI of the image to process
 * @returns Processed image ready for upload
 */
export const processImageForUpload = async (
  imageUri: string
): Promise<ImageData> => {
  try {
    // First correct orientation
    const orientedImage = await correctImageOrientation(imageUri);

    // Then compress
    const compressedImage = await compressImage(orientedImage.uri);

    return compressedImage;
  } catch (error) {
    throw new Error(
      `Image processing failed: ${error instanceof Error ? error.message : 'Unknown error'}`
    );
  }
};

/**
 * Convert image URI to blob for upload
 * @param imageUri - URI of the image
 * @returns Blob data ready for FormData upload
 */
export const imageUriToBlob = async (
  imageUri: string
): Promise<{ blob: Blob; filename: string }> => {
  try {
    const response = await fetch(imageUri);
    const blob = await response.blob();
    const timestamp = Date.now();
    const filename = `capture_${timestamp}.jpg`;

    return { blob, filename };
  } catch (error) {
    throw new Error(
      `Image blob conversion failed: ${error instanceof Error ? error.message : 'Unknown error'}`
    );
  }
};
