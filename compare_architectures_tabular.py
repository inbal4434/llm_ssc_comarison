#!/usr/bin/env python3
"""
Tabular Architecture Comparison Tool
====================================
Creates a flat table with binary indicators and detailed difference analysis.
Columns: Architecture | Services(1/0) | Components(1/0) | Attributes(1/0) | Configurations(1/0) 
         | Services_Differences | Components_Differences | Attributes_Differences | Configurations_Differences
         | Reasoning_Description
"""

import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class TabularComparisonRow:
    """Structure for each row in the tabular comparison"""

    architecture_id: str
    services_same: int  # 1 or 0
    components_same: int  # 1 or 0
    attributes_same: int  # 1 or 0
    configurations_same: int  # 1 or 0
    services_differences: str
    components_differences: str
    attributes_differences: str
    configurations_differences: str
    reasoning_description: str


class TabularArchitectureComparator:
    """Creates flat tabular comparison with binary indicators"""

    def __init__(
        self,
        baseline_file: Path,
        enhanced_file: Path,
        baseline_reasoning_file: Path,
        enhanced_reasoning_file: Path,
    ):
        self.baseline_data = self._load_json(baseline_file)
        self.enhanced_data = self._load_json(enhanced_file)
        self.baseline_reasoning = self._load_json(baseline_reasoning_file)
        self.enhanced_reasoning = self._load_json(enhanced_reasoning_file)

        # Create reasoning lookup tables
        self.baseline_reasoning_lookup = self._create_reasoning_lookup(
            self.baseline_reasoning
        )
        self.enhanced_reasoning_lookup = self._create_reasoning_lookup(
            self.enhanced_reasoning
        )

    def _load_json(self, file_path: Path) -> Dict:
        """Load JSON file with error handling"""
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return {}

    def _create_reasoning_lookup(self, reasoning_data: Dict) -> Dict:
        """Create lookup table for reasoning by service name"""
        lookup = {}
        for reasoning_obj in reasoning_data.get("reasoning_objects", []):
            service_name = reasoning_obj.get("service_codename")
            if service_name:
                lookup[service_name] = reasoning_obj
        return lookup

    def compare_all_architectures_tabular(self) -> List[TabularComparisonRow]:
        """Generate tabular comparison data"""
        baseline_archs = {
            arch["architecture_id"]: arch
            for arch in self.baseline_data.get("architectures", [])
        }
        enhanced_archs = {
            arch["architecture_id"]: arch
            for arch in self.enhanced_data.get("architectures", [])
        }

        all_arch_ids = sorted(set(baseline_archs.keys()) | set(enhanced_archs.keys()))

        print(
            f"🔍 Creating tabular comparison for {len(all_arch_ids)} architectures..."
        )

        comparison_rows = []

        for arch_id in all_arch_ids:
            print(f"  📋 Processing {arch_id}")
            baseline_arch = baseline_archs.get(arch_id)
            enhanced_arch = enhanced_archs.get(arch_id)

            row = self._create_comparison_row(arch_id, baseline_arch, enhanced_arch)
            comparison_rows.append(row)

        return comparison_rows

    def _create_comparison_row(
        self, arch_id: str, baseline_arch: Optional[Dict], enhanced_arch: Optional[Dict]
    ) -> TabularComparisonRow:
        """Create a single row of tabular comparison"""

        # Handle missing architectures
        if not baseline_arch:
            return TabularComparisonRow(
                architecture_id=arch_id,
                services_same=0,
                components_same=0,
                attributes_same=0,
                configurations_same=0,
                services_differences="Architecture only in enhanced",
                components_differences="Architecture only in enhanced",
                attributes_differences="Architecture only in enhanced",
                configurations_differences="Architecture only in enhanced",
                reasoning_description="Architecture exists only in enhanced dataset",
            )

        if not enhanced_arch:
            return TabularComparisonRow(
                architecture_id=arch_id,
                services_same=0,
                components_same=0,
                attributes_same=0,
                configurations_same=0,
                services_differences="Architecture only in baseline",
                components_differences="Architecture only in baseline",
                attributes_differences="Architecture only in baseline",
                configurations_differences="Architecture only in baseline",
                reasoning_description="Architecture exists only in baseline dataset",
            )

        # Extract architecture structures
        baseline_structure = self._extract_architecture_structure(baseline_arch)
        enhanced_structure = self._extract_architecture_structure(enhanced_arch)

        # Compare at each level
        services_comparison = self._compare_services_level(
            baseline_structure, enhanced_structure
        )
        components_comparison = self._compare_components_level(
            baseline_structure, enhanced_structure
        )
        attributes_comparison = self._compare_attributes_level(
            baseline_structure, enhanced_structure
        )
        configurations_comparison = self._compare_configurations_level(
            baseline_structure, enhanced_structure
        )

        # Get reasoning description
        reasoning_desc = self._get_reasoning_description(
            baseline_structure, enhanced_structure
        )

        return TabularComparisonRow(
            architecture_id=arch_id,
            services_same=1 if services_comparison["same"] else 0,
            components_same=1 if components_comparison["same"] else 0,
            attributes_same=1 if attributes_comparison["same"] else 0,
            configurations_same=1 if configurations_comparison["same"] else 0,
            services_differences=services_comparison["differences"],
            components_differences=components_comparison["differences"],
            attributes_differences=attributes_comparison["differences"],
            configurations_differences=configurations_comparison["differences"],
            reasoning_description=reasoning_desc,
        )

    def _extract_architecture_structure(self, arch_data: Dict) -> Dict:
        """Extract clean architecture structure for comparison"""
        if not arch_data:
            return {"services": {}}

        services = {}
        for component in arch_data.get("components_search_space", []):
            component_id = component.get("component_id", "")
            service_space = component.get("service_search_space", {})
            service_codename = service_space.get("service_codename", "Unknown")

            if service_codename not in services:
                services[service_codename] = {
                    "service_codename": service_codename,
                    "select_attributes": service_space.get(
                        "service_select_attributes", []
                    ),
                    "components": {},
                }

            # Add component details
            for service_component in service_space.get(
                "service_components_search_spaces", []
            ):
                comp_name = service_component.get(
                    "service_component_codename", "Unknown"
                )
                full_comp_name = f"{component_id}_{comp_name}"

                services[service_codename]["components"][full_comp_name] = {
                    "component_id": component_id,
                    "service_component_codename": comp_name,
                    "attributes_search_space": service_component.get(
                        "attributes_search_space", []
                    ),
                    "number_of_instances": service_component.get(
                        "number_of_instances", 1
                    ),
                    "service_component_sort": service_component.get(
                        "service_component_sort", []
                    ),
                }

        return {"services": services}

    def _compare_services_level(
        self, baseline_structure: Dict, enhanced_structure: Dict
    ) -> Dict:
        """Compare at services level"""
        baseline_services = set(baseline_structure["services"].keys())
        enhanced_services = set(enhanced_structure["services"].keys())

        same = baseline_services == enhanced_services
        differences = []

        if not same:
            baseline_only = baseline_services - enhanced_services
            enhanced_only = enhanced_services - baseline_services

            if baseline_only:
                differences.append(f"Baseline only: {', '.join(sorted(baseline_only))}")
            if enhanced_only:
                differences.append(f"Enhanced only: {', '.join(sorted(enhanced_only))}")

        return {
            "same": same,
            "differences": "; ".join(differences) if differences else "No differences",
        }

    def _compare_components_level(
        self, baseline_structure: Dict, enhanced_structure: Dict
    ) -> Dict:
        """Compare at components level"""
        baseline_components = {}
        enhanced_components = {}

        # Flatten all components across services
        for service_name, service_data in baseline_structure["services"].items():
            for comp_name, comp_data in service_data["components"].items():
                baseline_components[f"{service_name}::{comp_name}"] = comp_data

        for service_name, service_data in enhanced_structure["services"].items():
            for comp_name, comp_data in service_data["components"].items():
                enhanced_components[f"{service_name}::{comp_name}"] = comp_data

        baseline_comp_keys = set(baseline_components.keys())
        enhanced_comp_keys = set(enhanced_components.keys())

        same = baseline_comp_keys == enhanced_comp_keys
        differences = []

        if not same:
            baseline_only = baseline_comp_keys - enhanced_comp_keys
            enhanced_only = enhanced_comp_keys - baseline_comp_keys

            if baseline_only:
                differences.append(f"Baseline only: {', '.join(sorted(baseline_only))}")
            if enhanced_only:
                differences.append(f"Enhanced only: {', '.join(sorted(enhanced_only))}")

        return {
            "same": same,
            "differences": "; ".join(differences) if differences else "No differences",
        }

    def _compare_attributes_level(
        self, baseline_structure: Dict, enhanced_structure: Dict
    ) -> Dict:
        """Compare at attributes level"""
        baseline_attrs = self._get_all_attributes(baseline_structure)
        enhanced_attrs = self._get_all_attributes(enhanced_structure)

        same = baseline_attrs == enhanced_attrs
        differences = []

        if not same:
            # Compare each component's attributes
            all_comp_keys = set(baseline_attrs.keys()) | set(enhanced_attrs.keys())
            for comp_key in all_comp_keys:
                baseline_comp_attrs = baseline_attrs.get(comp_key, {})
                enhanced_comp_attrs = enhanced_attrs.get(comp_key, {})

                if baseline_comp_attrs != enhanced_comp_attrs:
                    baseline_attr_names = set(baseline_comp_attrs.keys())
                    enhanced_attr_names = set(enhanced_comp_attrs.keys())

                    if baseline_attr_names != enhanced_attr_names:
                        baseline_only = baseline_attr_names - enhanced_attr_names
                        enhanced_only = enhanced_attr_names - baseline_attr_names

                        if baseline_only or enhanced_only:
                            comp_diffs = []
                            if baseline_only:
                                comp_diffs.append(
                                    f"baseline only: {', '.join(sorted(baseline_only))}"
                                )
                            if enhanced_only:
                                comp_diffs.append(
                                    f"enhanced only: {', '.join(sorted(enhanced_only))}"
                                )
                            differences.append(f"{comp_key} ({'; '.join(comp_diffs)})")

        return {
            "same": same,
            "differences": "; ".join(differences) if differences else "No differences",
        }

    def _compare_configurations_level(
        self, baseline_structure: Dict, enhanced_structure: Dict
    ) -> Dict:
        """Compare at configurations level (attribute values, constraints, etc.)"""
        baseline_configs = self._get_all_configurations(baseline_structure)
        enhanced_configs = self._get_all_configurations(enhanced_structure)

        same = baseline_configs == enhanced_configs
        differences = []

        if not same:
            all_comp_keys = set(baseline_configs.keys()) | set(enhanced_configs.keys())
            for comp_key in all_comp_keys:
                baseline_comp_configs = baseline_configs.get(comp_key, {})
                enhanced_comp_configs = enhanced_configs.get(comp_key, {})

                if baseline_comp_configs != enhanced_comp_configs:
                    comp_diffs = []

                    # Compare number of instances
                    if baseline_comp_configs.get(
                        "instances"
                    ) != enhanced_comp_configs.get("instances"):
                        comp_diffs.append(
                            f"instances: {baseline_comp_configs.get('instances')} vs {enhanced_comp_configs.get('instances')}"
                        )

                    # Compare sort configuration
                    if baseline_comp_configs.get("sort") != enhanced_comp_configs.get(
                        "sort"
                    ):
                        comp_diffs.append("sort configuration differs")

                    # Compare attribute configurations
                    baseline_attr_configs = baseline_comp_configs.get("attributes", {})
                    enhanced_attr_configs = enhanced_comp_configs.get("attributes", {})

                    for attr_name in set(baseline_attr_configs.keys()) | set(
                        enhanced_attr_configs.keys()
                    ):
                        baseline_attr = baseline_attr_configs.get(attr_name, {})
                        enhanced_attr = enhanced_attr_configs.get(attr_name, {})

                        if baseline_attr != enhanced_attr:
                            attr_diffs = []
                            if baseline_attr.get("values") != enhanced_attr.get(
                                "values"
                            ):
                                attr_diffs.append("values")
                            if baseline_attr.get("constraint") != enhanced_attr.get(
                                "constraint"
                            ):
                                attr_diffs.append("constraint")
                            if baseline_attr.get("unit") != enhanced_attr.get("unit"):
                                attr_diffs.append("unit")

                            if attr_diffs:
                                comp_diffs.append(
                                    f"{attr_name}: {', '.join(attr_diffs)}"
                                )

                    if comp_diffs:
                        differences.append(f"{comp_key} ({'; '.join(comp_diffs)})")

        return {
            "same": same,
            "differences": "; ".join(differences) if differences else "No differences",
        }

    def _get_all_attributes(self, structure: Dict) -> Dict:
        """Extract all attributes for comparison"""
        attributes = {}

        for service_name, service_data in structure["services"].items():
            for comp_name, comp_data in service_data["components"].items():
                comp_key = f"{service_name}::{comp_name}"
                attributes[comp_key] = {}

                for attr in comp_data.get("attributes_search_space", []):
                    attr_name = attr.get("attribute_codename", "unknown")
                    attributes[comp_key][attr_name] = {
                        "codename": attr_name,
                        "exists": True,
                    }

        return attributes

    def _get_all_configurations(self, structure: Dict) -> Dict:
        """Extract all configurations for detailed comparison"""
        configurations = {}

        for service_name, service_data in structure["services"].items():
            for comp_name, comp_data in service_data["components"].items():
                comp_key = f"{service_name}::{comp_name}"
                configurations[comp_key] = {
                    "instances": comp_data.get("number_of_instances"),
                    "sort": comp_data.get("service_component_sort", []),
                    "attributes": {},
                }

                for attr in comp_data.get("attributes_search_space", []):
                    attr_name = attr.get("attribute_codename", "unknown")
                    configurations[comp_key]["attributes"][attr_name] = {
                        "values": attr.get("attribute_values"),
                        "constraint": attr.get("attribute_constraint_expr"),
                        "unit": attr.get("attribute_unit"),
                    }

        return configurations

    def _get_reasoning_description(
        self, baseline_structure: Dict, enhanced_structure: Dict
    ) -> str:
        """Generate reasoning description from reasoning files with specific insights about why choices were made"""
        descriptions = []

        # Get service names from both structures
        baseline_services = set(baseline_structure["services"].keys())
        enhanced_services = set(enhanced_structure["services"].keys())
        all_services = baseline_services | enhanced_services

        for service_name in all_services:
            baseline_reasoning = self.baseline_reasoning_lookup.get(service_name, {})
            enhanced_reasoning = self.enhanced_reasoning_lookup.get(service_name, {})

            # Extract specific decision rationales
            baseline_attr_rationale = baseline_reasoning.get(
                "attribute_selection_rationale", ""
            )
            enhanced_attr_rationale = enhanced_reasoning.get(
                "attribute_selection_rationale", ""
            )

            baseline_critical_attrs = baseline_reasoning.get(
                "critical_attributes_reasoning", ""
            )
            enhanced_critical_attrs = enhanced_reasoning.get(
                "critical_attributes_reasoning", ""
            )

            baseline_alternatives = baseline_reasoning.get(
                "alternatives_considered", []
            )
            enhanced_alternatives = enhanced_reasoning.get(
                "alternatives_considered", []
            )

            # If service exists in both, compare decision rationales
            if service_name in baseline_services and service_name in enhanced_services:
                insights = []

                # Compare attribute selection rationale
                if baseline_attr_rationale != enhanced_attr_rationale:
                    if enhanced_attr_rationale:
                        # Extract key insight from enhanced rationale
                        key_insight = self._extract_key_insight(
                            enhanced_attr_rationale, "Enhanced reasoning"
                        )
                        if key_insight:
                            insights.append(f"Attribute selection: {key_insight}")

                # Compare critical attributes reasoning
                if baseline_critical_attrs != enhanced_critical_attrs:
                    if enhanced_critical_attrs:
                        key_insight = self._extract_key_insight(
                            enhanced_critical_attrs, "Critical attributes"
                        )
                        if key_insight:
                            insights.append(f"Critical attributes: {key_insight}")

                # Compare alternatives considered
                if baseline_alternatives != enhanced_alternatives:
                    if enhanced_alternatives and len(enhanced_alternatives) > 0:
                        # Get the first alternative reasoning
                        alt_reasoning = (
                            enhanced_alternatives[0]
                            if isinstance(enhanced_alternatives[0], str)
                            else str(enhanced_alternatives[0])
                        )
                        key_insight = self._extract_key_insight(
                            alt_reasoning, "Alternative considered"
                        )
                        if key_insight:
                            insights.append(f"Design choice: {key_insight}")

                if insights:
                    descriptions.append(f"{service_name}: {'; '.join(insights)}")

            # If service exists only in one dataset, provide reasoning for why it was included
            elif (
                service_name in enhanced_services
                and service_name not in baseline_services
            ):
                enhanced_understanding = enhanced_reasoning.get(
                    "service_understanding", ""
                )
                if enhanced_understanding:
                    key_insight = self._extract_key_insight(
                        enhanced_understanding, "Service purpose"
                    )
                    if key_insight:
                        descriptions.append(
                            f"{service_name} (Enhanced only): {key_insight}"
                        )

                # Also include why this service was chosen
                if enhanced_attr_rationale:
                    choice_insight = self._extract_key_insight(
                        enhanced_attr_rationale, "Selection rationale"
                    )
                    if choice_insight:
                        descriptions.append(
                            f"{service_name} selection reasoning: {choice_insight}"
                        )

            elif (
                service_name in baseline_services
                and service_name not in enhanced_services
            ):
                baseline_understanding = baseline_reasoning.get(
                    "service_understanding", ""
                )
                if baseline_understanding:
                    key_insight = self._extract_key_insight(
                        baseline_understanding, "Service purpose"
                    )
                    if key_insight:
                        descriptions.append(
                            f"{service_name} (Baseline only): {key_insight}"
                        )

        # If no differences found, provide insights from common services about their configuration choices
        if not descriptions:
            common_services = baseline_services & enhanced_services
            for service_name in list(common_services)[
                :2
            ]:  # Get insights from first 2 services
                reasoning = self.enhanced_reasoning_lookup.get(
                    service_name, {}
                ) or self.baseline_reasoning_lookup.get(service_name, {})

                # Get insights about why specific configurations were chosen
                attr_rationale = reasoning.get("attribute_selection_rationale", "")
                critical_attrs = reasoning.get("critical_attributes_reasoning", "")

                if attr_rationale:
                    key_insight = self._extract_key_insight(
                        attr_rationale, "Configuration rationale"
                    )
                    if key_insight:
                        descriptions.append(f"{service_name}: {key_insight}")
                elif critical_attrs:
                    key_insight = self._extract_key_insight(
                        critical_attrs, "Critical reasoning"
                    )
                    if key_insight:
                        descriptions.append(f"{service_name}: {key_insight}")

        return (
            "; ".join(descriptions)
            if descriptions
            else "No specific reasoning insights available"
        )

    def _extract_key_insight(self, text: str, context: str) -> str:
        """Extract key insight from reasoning text"""
        if not text:
            return ""

        # Clean up the text
        text = text.strip()

        # Look for key phrases that indicate decision rationale
        key_phrases = [
            "because",
            "due to",
            "in order to",
            "to ensure",
            "chosen to",
            "selected to",
            "prioritized",
            "optimized for",
            "designed for",
            "configured for",
            "focused on",
            "enables",
            "allows",
            "provides",
            "ensures",
            "guarantees",
            "supports",
        ]

        sentences = text.split(". ")

        # Find sentences with key decision-making phrases
        key_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if any(phrase in sentence.lower() for phrase in key_phrases):
                # Clean up the sentence
                if sentence and not sentence.endswith("."):
                    sentence += "."
                key_sentences.append(sentence)

        # If we found key sentences, use the first one (usually most important)
        if key_sentences:
            return key_sentences[0][:150] + (
                "..." if len(key_sentences[0]) > 150 else ""
            )

        # Otherwise, take the first meaningful sentence
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 30:  # Avoid very short sentences
                return sentence[:150] + ("..." if len(sentence) > 150 else "")

        # Fallback to first part of text
        return text[:150] + ("..." if len(text) > 150 else "")

    def export_tabular_comparison(self, output_file: Path) -> pd.DataFrame:
        """Export tabular comparison to CSV"""
        comparison_rows = self.compare_all_architectures_tabular()

        # Convert to DataFrame
        df_data = []
        for row in comparison_rows:
            df_data.append(
                {
                    "Architecture": row.architecture_id,
                    "Services_Same": row.services_same,
                    "Components_Same": row.components_same,
                    "Attributes_Same": row.attributes_same,
                    "Configurations_Same": row.configurations_same,
                    "Services_Differences": row.services_differences,
                    "Components_Differences": row.components_differences,
                    "Attributes_Differences": row.attributes_differences,
                    "Configurations_Differences": row.configurations_differences,
                    "Reasoning_Description": row.reasoning_description,
                }
            )

        df = pd.DataFrame(df_data)

        # Save to CSV
        df.to_csv(output_file, index=False)
        print(f"✅ Tabular comparison exported to: {output_file}")

        # Print summary stats
        total_archs = len(df)
        services_same_count = df["Services_Same"].sum()
        components_same_count = df["Components_Same"].sum()
        attributes_same_count = df["Attributes_Same"].sum()
        configurations_same_count = df["Configurations_Same"].sum()

        print(f"\n📊 Summary Statistics:")
        print(f"   Total Architectures: {total_archs}")
        print(
            f"   Services Same: {services_same_count}/{total_archs} ({services_same_count/total_archs*100:.1f}%)"
        )
        print(
            f"   Components Same: {components_same_count}/{total_archs} ({components_same_count/total_archs*100:.1f}%)"
        )
        print(
            f"   Attributes Same: {attributes_same_count}/{total_archs} ({attributes_same_count/total_archs*100:.1f}%)"
        )
        print(
            f"   Configurations Same: {configurations_same_count}/{total_archs} ({configurations_same_count/total_archs*100:.1f}%)"
        )

        return df


def main():
    """Main execution function"""
    print("📊 Tabular Architecture Comparison")
    print("=" * 50)

    # File paths
    baseline_file = Path(
        "comparison_output/baseline_db_architectures_set_search_space_output.json"
    )
    enhanced_file = Path(
        "comparison_output/enhanced_db_architectures_set_search_space_output.json"
    )
    baseline_reasoning_file = Path(
        "comparison_output/baseline_db_architectures_set_search_space_reasoning_output.json"
    )
    enhanced_reasoning_file = Path(
        "comparison_output/enhanced_db_architectures_set_search_space_reasoning_output.json"
    )

    # Initialize comparator
    comparator = TabularArchitectureComparator(
        baseline_file, enhanced_file, baseline_reasoning_file, enhanced_reasoning_file
    )

    # Run comparison and export
    output_file = Path("comparison_output/tabular_architecture_comparison.csv")
    df = comparator.export_tabular_comparison(output_file)

    print(f"\n🎉 Tabular comparison complete!")
    print(f"   Output file: {output_file}")
    if df is not None:
        print(f"   Rows: {len(df)}")
        print(f"   Columns: {len(df.columns)}")
    else:
        print("   No data generated")


if __name__ == "__main__":
    main()
