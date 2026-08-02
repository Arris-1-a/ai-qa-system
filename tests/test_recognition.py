

class TestImageEnhancer:
    def test_enhance_brightness(self):
        """Test brightness enhancement."""
        from main import ImageEnhancer
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        result = ImageEnhancer.enhance_brightness(img, factor=1.5)
        assert result is not None
    
    def test_enhance_contrast(self):
        """Test contrast enhancement."""
        from main import ImageEnhancer
        img = np.ones((100, 100, 3), dtype=np.uint8) * 128
        result = ImageEnhancer.enhance_contrast(img, alpha=1.5)
        assert result is not None
    
    def test_sharpen(self):
        """Test sharpening."""
        from main import ImageEnhancer
        img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        result = ImageEnhancer.sharpen(img)
        assert result is not None
    
    def test_resize_keep_aspect(self):
        """Test aspect ratio preservation."""
        from main import ImageEnhancer
        img = np.zeros((200, 100, 3), dtype=np.uint8)
        result, scale = ImageEnhancer.resize_keep_aspect(img, max_size=50)
        assert result.shape[1] <= 50
        assert result.shape[0] <= 50
