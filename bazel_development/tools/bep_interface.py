#!/usr/bin/env python3
"""
bep_interface.py - Object-oriented interface for Bazel Build Event Protocol (BEP)

This module can be imported as a library into other scripts.
It parses BEP JSON files (generated with --build_event_json_file=bep.json)
and extracts test results with framework and component information.

Usage:
    from bep_interface import BepInterface

    bep = BepInterface("bep.json")
    results = bep.get_test_results()
    
    for result in results:
        print(f"Label: {result['label']}")
        print(f"Framework: {result['framework']}")
        print(f"Component: {result['component']}")
        print(f"XML Path: {result['xml_path']}")
        print(f"Start: {result['first_start_time']}")
        print(f"Stop: {result['last_stop_time']}")
"""

import json
from typing import List, Dict, Optional, Any, Iterator


class BepInterface:
    """
    Object-oriented interface for parsing Bazel Build Event Protocol (BEP) files.
    
    Attributes:
        bep_file: Path to the BEP JSON file
        events: List of all loaded events
    """
    
    def __init__(self, bep_file: str):
        """
        Initializes the BEP interface and loads the events.
        
        Args:
            bep_file: Path to the BEP JSON file (generated with --build_event_json_file)
        """
        self.bep_file = bep_file
        self.events: List[Dict[str, Any]] = []
        self._tags_by_label: Dict[str, List[str]] = {}
        self._summaries_by_label: Dict[str, Dict[str, Any]] = {}
        self._results_by_label: Dict[str, Dict[str, Any]] = {}
        
        self._load_events()
        self._index_events()
    
    def _load_events(self) -> None:
        """Loads all events from the BEP file (NDJSON format)."""
        self.events = []
        with open(self.bep_file, "r", encoding="utf-8") as f:
            for lineno, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                    self.events.append(event)
                except json.JSONDecodeError as exc:
                    # Print warning but don't abort
                    print(f"Warning: Line {lineno} is not valid JSON ({exc})")
    
    def _index_events(self) -> None:
        """Indexes events by label for fast access."""
        # Collect tags from targetConfigured events
        for event in self.events:
            if 'configured' in event and 'targetConfigured' in event.get('id', {}):
                label = event['id']['targetConfigured'].get('label')
                tags = event.get('configured', {}).get('tag', [])
                if label:
                    self._tags_by_label[label] = tags
        
        # Collect testSummary events
        for event in self.events:
            test_summary = event.get("testSummary")
            if test_summary is not None:
                event_id = event.get("id", {})
                ts_id = event_id.get("testSummary", {})
                label = ts_id.get("label")
                if label:
                    self._summaries_by_label[label] = test_summary
        
        # Collect testResult events
        for event in self.events:
            test_result = event.get("testResult")
            if test_result is not None:
                event_id = event.get("id", {})
                tr_id = event_id.get("testResult", {})
                label = tr_id.get("label")
                if label:
                    self._results_by_label[label] = test_result
    
    @staticmethod
    def _parse_tag(tags: List[str], prefix: str) -> Optional[str]:
        """
        Extracts a value from tags with the given prefix.
        
        Args:
            tags: List of tags (e.g., ["framework:pytest", "component:JsonPreprocessor"])
            prefix: Prefix to search for (e.g., "framework:")
            
        Returns:
            Value after the prefix or None if not found
        """
        for tag in tags:
            if tag.startswith(prefix):
                return tag[len(prefix):]
        return None
    
    @staticmethod
    def _extract_xml_path(test_result: Dict[str, Any]) -> Optional[str]:
        """
        Extracts the path to test.xml from testResult.
        
        Args:
            test_result: The testResult dictionary from the BEP event
            
        Returns:
            Path to the XML file or None
        """
        for output in test_result.get("testActionOutput", []):
            if output.get("name") == "test.xml":
                uri = output.get("uri", "")
                # Remove file:// prefix
                if uri.startswith("file://"):
                    return uri[len("file://"):]
                return uri
        return None
    
    def get_test_results(
        self,
        only_failed: bool = False,
        label_filter: Optional[str] = None,
        framework_filter: Optional[str] = None,
        component_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Returns a list of test results with framework and component information.
        
        Each dictionary contains:
            - label: Target label (e.g., "//pkg:test")
            - xml_path: Path to the XML log file
            - framework: Name of the test framework (from tag "framework:<name>") or None
            - component: Name of the component (from tag "component:<name>") or None
            - first_start_time: Start timestamp (ISO 8601)
            - last_stop_time: End timestamp (ISO 8601)
            - status: Test status (PASSED, FAILED, etc.)
            - duration_ms: Test duration in milliseconds
            - cached: True if test result came from any cache (most reliable indicator)
            - cache_source: Cache source ("local_action_cache", "disk_or_remote_cache", "none")
            - cached_locally: True if from local action cache (in output base)
            - cached_remotely: True if from remote cache (if reported by Bazel)
            - total_num_cached: Number of test runs from cache (from testSummary)
            - tags: Complete tag list
        
        Note on cache detection:
            - `cached` is the most reliable indicator (based on totalNumCached > 0)
            - `cached_locally` only indicates the local action cache, not disk cache
            - After `bazel clean --expunge`, disk cache hits show as:
              cached_locally=False but totalNumCached=1
        
        Args:
            only_failed: Only return failed tests
            label_filter: Only tests with this label
            framework_filter: Only tests with this framework
            component_filter: Only tests with this component
            
        Returns:
            List of dictionaries with test results
        """
        results = []
        
        # Only labels with actual test results (testResult or testSummary)
        # Non-test targets have neither testResult nor testSummary
        test_labels = set(self._results_by_label.keys()) | set(self._summaries_by_label.keys())
        
        for label in test_labels:
            tags = self._tags_by_label.get(label, [])
            test_result = self._results_by_label.get(label, {})
            test_summary = self._summaries_by_label.get(label, {})
            
            # Extract framework and component from tags
            framework = self._parse_tag(tags, "framework:")
            component = self._parse_tag(tags, "component:")
            
            # Extract XML path
            xml_path = self._extract_xml_path(test_result)
            
            # Determine status (from testResult or testSummary)
            status = test_result.get("status") or test_summary.get("overallStatus", "UNKNOWN")
            
            # Timestamps from testSummary
            first_start_time = test_summary.get("firstStartTime")
            last_stop_time = test_summary.get("lastStopTime")
            
            # Duration from testResult
            duration_ms = test_result.get("testAttemptDurationMillis")
            
            # Cache information from testResult
            cached_locally = test_result.get("cachedLocally", False)
            cached_remotely = test_result.get("remotelyCached", False)
            
            # Cache counter from testSummary
            total_num_cached = test_summary.get("totalNumCached", 0)
            
            # Derived cache status (most reliable indicator)
            # totalNumCached > 0 means the result came from some cache
            # (local action cache, disk cache, or remote cache)
            cached = total_num_cached > 0
            
            # Determine cache source
            if cached_locally:
                cache_source = "local_action_cache"
            elif cached and not cached_locally:
                # Cached but not in local action cache = disk cache or remote cache
                cache_source = "disk_or_remote_cache"
            else:
                cache_source = "none"
            
            result_entry = {
                "label": label,
                "xml_path": xml_path,
                "framework": framework,
                "component": component,
                "first_start_time": first_start_time,
                "last_stop_time": last_stop_time,
                "status": status,
                "duration_ms": duration_ms,
                "cached": cached,
                "cache_source": cache_source,
                "cached_locally": cached_locally,
                "cached_remotely": cached_remotely,
                "total_num_cached": total_num_cached,
                "tags": tags,
            }
            
            # Apply filters
            if only_failed and status == "PASSED":
                continue
            if label_filter and label != label_filter:
                continue
            if framework_filter and framework != framework_filter:
                continue
            if component_filter and component != component_filter:
                continue
            
            results.append(result_entry)
        
        return results
    
    def get_test_summaries(
        self,
        only_failed: bool = False,
        label_filter: Optional[str] = None,
        include_tags: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Returns aggregated test results per target.
        
        Args:
            only_failed: Only failed tests
            label_filter: Only tests with this label
            include_tags: Include tags
            
        Returns:
            List of dictionaries with test summaries
        """
        summaries = []
        
        for event in self.events:
            test_summary = event.get("testSummary")
            if test_summary is None:
                continue
            
            event_id = event.get("id", {})
            ts_id = event_id.get("testSummary", {})
            label = ts_id.get("label", "unknown")
            
            tags = self._tags_by_label.get(label, [])
            overall_status = test_summary.get("overallStatus", "UNKNOWN")
            
            # Apply filters
            if only_failed and overall_status == "PASSED":
                continue
            if label_filter and label != label_filter:
                continue
            
            entry = {
                "label": label,
                "overall_status": overall_status,
                "total_run_count": test_summary.get("totalRunCount"),
                "total_num_cached": test_summary.get("totalNumCached"),
                "num_passed": len(test_summary.get("passed", [])),
                "num_failed": len(test_summary.get("failed", [])),
                "first_start_time": test_summary.get("firstStartTime"),
                "last_stop_time": test_summary.get("lastStopTime"),
                "total_run_duration_ms": test_summary.get("totalRunDurationMillis"),
            }
            
            if include_tags:
                entry["tags"] = tags
                entry["framework"] = self._parse_tag(tags, "framework:")
                entry["component"] = self._parse_tag(tags, "component:")
            
            summaries.append(entry)
        
        return summaries
    
    def get_junit_xml_paths(
        self,
        only_failed: bool = False,
        label_filter: Optional[str] = None,
        include_tags: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Returns a list of all JUnit XML test results (test.xml).
        
        Args:
            only_failed: Only failed tests
            label_filter: Only tests with this label
            include_tags: Include tags
            
        Returns:
            List of dictionaries with XML paths and metadata
        """
        rows = []
        
        for event in self.events:
            test_result = event.get("testResult")
            if test_result is None:
                continue
            
            event_id = event.get("id", {})
            tr_id = event_id.get("testResult", {})
            label = tr_id.get("label", "unknown")
            status = test_result.get("status", "UNKNOWN")
            
            # Apply filters
            if only_failed and status == "PASSED":
                continue
            if label_filter and label != label_filter:
                continue
            
            tags = self._tags_by_label.get(label, [])
            
            for out in test_result.get("testActionOutput", []):
                name = out.get("name", "")
                if name != "test.xml":
                    continue
                
                uri = out.get("uri", "")
                path = uri[len("file://"):] if uri.startswith("file://") else uri
                
                entry = {
                    "label": label,
                    "run": tr_id.get("run"),
                    "shard": tr_id.get("shard"),
                    "attempt": tr_id.get("attempt"),
                    "status": status,
                    "name": name,
                    "path": path,
                }
                
                if include_tags:
                    entry["tags"] = tags
                    entry["framework"] = self._parse_tag(tags, "framework:")
                    entry["component"] = self._parse_tag(tags, "component:")
                
                rows.append(entry)
        
        return rows
    
    def get_labels(self) -> List[str]:
        """
        Returns a list of all test labels.
        
        Returns:
            List of target labels
        """
        return list(set(self._tags_by_label.keys()) | set(self._results_by_label.keys()))
    
    def get_tags_for_label(self, label: str) -> List[str]:
        """
        Returns the tags for a specific label.
        
        Args:
            label: Target label
            
        Returns:
            List of tags or empty list
        """
        return self._tags_by_label.get(label, [])
    
    def get_framework_for_label(self, label: str) -> Optional[str]:
        """
        Returns the framework for a specific label.
        
        Args:
            label: Target label
            
        Returns:
            Framework name or None
        """
        tags = self._tags_by_label.get(label, [])
        return self._parse_tag(tags, "framework:")
    
    def get_component_for_label(self, label: str) -> Optional[str]:
        """
        Returns the component for a specific label.
        
        Args:
            label: Target label
            
        Returns:
            Component name or None
        """
        tags = self._tags_by_label.get(label, [])
        return self._parse_tag(tags, "component:")


# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python bep_interface.py <bep.json>")
        print()
        print("Example:")
        print("  python bep_interface.py bep.json")
        sys.exit(1)
    
    bep_file = sys.argv[1]
    
    # Create interface
    bep = BepInterface(bep_file)
    
    # Get test results
    results = bep.get_test_results()
    
    print()
    print(f"Found test results: {len(results)}")
    print()
    
    for result in results:
        print(f"Label             : {result['label']}")
        print(f"  Status          : {result['status']}")
        print(f"  Framework       : {result['framework']}")
        print(f"  Component       : {result['component']}")
        print(f"  XML Path        : {result['xml_path']}")
        print(f"  Start           : {result['first_start_time']}")
        print(f"  Stop            : {result['last_stop_time']}")
        print(f"  Duration        : {result['duration_ms']} ms")
        print(f"  Cached          : {result['cached']}")
        print(f"  Cache Source    : {result['cache_source']}")
        print(f"  Cached Locally  : {result['cached_locally']}")
        print(f"  Cached Remotely : {result['cached_remotely']}")
        print(f"  Total Cached    : {result['total_num_cached']}")
        print(f"  Tags            : {result['tags']}")
        print()
