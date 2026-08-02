

class TestDocumentValidator:
    def test_empty_document(self):
        """Test validation of empty document."""
        from main import DocumentValidator
        errors = DocumentValidator.validate("", "test.txt")
        assert len(errors) > 0
        assert "empty" in errors[0].lower()
    
    def test_large_document(self, tmp_path):
        """Test validation of large document."""
        from main import DocumentValidator
        large_file = tmp_path / "large.txt"
        large_file.write_text("x" * (11 * 1024 * 1024))  # 11MB
        errors = DocumentValidator.validate(large_file.read_text(), str(large_file))
        assert len(errors) > 0
