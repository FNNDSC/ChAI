# Leg Length Discrepancy Full Workflow v20240705

**Authors:** Rudolph Pienaar [dev@babymri.org](mailto:dev@babymri.org)
**Category:** Imaging
**Locked:** false

**Description:**
Perform the full leg length workflow, including joins.

---

## Workflow Overview

This pipeline ingests DICOM images of lower limbs and processes them through a sequence of plugins to produce both heatmap visualizations of anatomical landmarks and quantitative measurements. Finally, the results are packaged into DICOM format and pushed to a PACS server.

## Pipeline Definition (YAML)

```yaml
authors: Rudolph Pienaar <dev@babymri.org>
name: "Leg Length Discrepancy Full Workflow v20240705"
description: "Perform the full leg length workflow, including joins"
category: Imaging
locked: false
plugin_tree:
  # see detailed step list below
```

## Detailed Steps

1. **root-0**

   * **Plugin:** `pl-simpledsapp v2.1.0`
   * **Description:** Core node that holds the input DICOM files. This is the branching point for subsequent processing.

2. **dcm-to-mha-1**

   * **Plugin:** `pl-dcm2mha_cnvtr v1.2.24`
   * **Inputs:** Inherits DICOMs from `root-0`.
   * **Parameters:**

     * `inputFileFilter`: `"**/*.dcm"`
     * `rotate`: `90`
     * `imageName`: `'composite.png'`
     * `filterPerc`: `30`
   * **Description:** Converts DICOM images to MetaImage (MHA) format for compatibility with downstream inference.

3. **generate-landmark-heatmaps-2**

   * **Plugin:** `pl-lld_inference v2.2.11`
   * **Inputs:** MHA images from `dcm-to-mha-1`.
   * **Parameters:**

     * `inputFileFilter`: `"**/*.mha"`
     * `heatmapThreshold`: `'0.5'`
   * **Description:** Runs an inference model to detect anatomical landmarks and outputs heatmap overlays.

4. **heatmaps-join-root-3**

   * **Plugin:** `pl-topologicalcopy v1.0.2`
   * **Inputs:** Branches from `root-0` and `generate-landmark-heatmaps-2`.
   * **Parameters:**

     * `plugininstances`: `root-0,generate-landmark-heatmaps-2`
     * `filter`: `\.dcm$,\.csv$`
   * **Description:** Joins original DICOM files with CSV outputs from inference for a combined dataset.

5. **landmarks-to-json-4**

   * **Plugin:** `pl-csv2json v1.2.4`
   * **Inputs:** CSVs from `heatmaps-join-root-3`.
   * **Parameters:**

     * `inputFileFilter`: `"**/*.csv"`
     * `outputFileStem`: `"prediction"`
     * `addTags`: `"PatientID,PatientName,PatientAge,StudyDate"`
   * **Description:** Converts CSV landmark coordinates into JSON format, adding patient metadata tags.

6. **heatmaps-join-json-5**

   * **Plugin:** `pl-topologicalcopy v1.0.2`
   * **Inputs:** Heatmap images (`generate-landmark-heatmaps-2`) and JSON (`landmarks-to-json-4`).
   * **Parameters:**

     * `plugininstances`: `generate-landmark-heatmaps-2,landmarks-to-json-4`
     * `filter`: `\.jpg$,\.json$`
   * **Description:** Merges the visual heatmaps with the corresponding JSON data for combined output.

7. **measure-leg-segments-6**

   * **Plugin:** `pl-markimg v1.4.8`
   * **Inputs:** Joined outputs from `heatmaps-join-json-5`.
   * **Parameters:**

     * `inputImageName`: `"input.jpg"`
     * `pointMarker`: `"."`
     * `pointSize`: `10`
     * `linewidth`: `0.5`
     * `lineGap`: `70`
     * `addText`: `"Not for diagnostic use"`
     * `addTextPos`: `bottom`
     * `addTextSize`: `5`
     * `addTextColor`: `darkred`
   * **Description:** Calculates distances between landmark points, annotates measurements on the image, and outputs both image and JSON report.

8. **measurement-join-dicom-7**

   * **Plugin:** `pl-topologicalcopy v1.0.2`
   * **Inputs:** Combined original DICOM/CSV (`heatmaps-join-root-3`) and measurements (`measure-leg-segments-6`).
   * **Parameters:**

     * `plugininstances`: `heatmaps-join-root-3,measure-leg-segments-6`
     * `filter`: `\.dcm$,\.png$`
   * **Description:** Aggregates annotated images with original DICOM context for final conversion.

9. **image-to-DICOM-8**

   * **Plugin:** `pl-dicommake v2.3.2`
   * **Inputs:** PNG images from `measurement-join-dicom-7`.
   * **Parameters:**

     * `filterIMG`: `"**/*.png"`
     * `outputSubDir`: `data`
     * `thread`: `true`
   * **Description:** Converts annotated PNGs back into DICOM files, preserving metadata.

10. **pacs-push-9**

    * **Plugin:** `pl-dicom_dirsend v1.1.2`
    * **Inputs:** Generated DICOMs from `image-to-DICOM-8`.
    * **Parameters:**

      * `fileFilter`: `"dcm"`
      * `host`: `0.0.0.0`
      * `port`: `104`
      * `aetTitle`: `"SYNAPSERESEARCH"`
    * **Description:** Pushes the final DICOMs to the designated PACS server.

---

*End of workflow definition.*
