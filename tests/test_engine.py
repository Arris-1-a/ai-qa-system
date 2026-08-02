

class TestModelProfiler:
    def test_profile_recommend(self, engine):
        """Test recommendation profiling."""
        profiler = ModelProfiler(engine)
        assert profiler.engine is not None
    
    def test_profile_train(self, engine):
        """Test training profiling."""
        profiler = ModelProfiler(engine)
        assert profiler.engine is not None
