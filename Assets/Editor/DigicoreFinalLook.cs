#if UNITY_EDITOR
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

public static class DigicoreFinalLook
{
    private const string ScenePath = "Assets/Scenes/DigicoreDream.unity";

    [MenuItem("Tools/ML/Generate Digicore Final Look")]
    public static void GenerateFinalLook()
    {
        DigicoreSceneGenerator.Generate();
        var scene = EditorSceneManager.GetActiveScene();

        Shader glitchShader = Shader.Find("ML/DigicoreGlitch");
        Material magenta = CreateGlitchMaterial("FinalMagenta", new Color(0.55f, 0.01f, 0.72f), new Color(1f, 0.01f, 0.65f) * 3.2f, glitchShader);
        Material cyan = CreateGlitchMaterial("FinalCyan", new Color(0.01f, 0.28f, 0.6f), new Color(0.05f, 0.85f, 1f) * 4f, glitchShader);
        Material white = CreateGlitchMaterial("FinalWhite", new Color(0.7f, 0.7f, 0.9f), Color.white * 3f, glitchShader);

        foreach (var renderer in Object.FindObjectsByType<Renderer>(FindObjectsSortMode.None))
        {
            if (renderer.name.Contains("GlitchShard"))
            {
                renderer.sharedMaterial = Random.value > 0.5f ? magenta : cyan;
                if (renderer.GetComponent<GlitchPulse>() == null)
                    renderer.gameObject.AddComponent<GlitchPulse>();
            }
        }

        CreateSkyCeiling(magenta, cyan);
        CreateSparkField(white, magenta, cyan);
        CreateDistantTower(magenta, cyan);
        UpgradeCamera();
        UpgradeVolume();

        EditorSceneManager.SaveScene(scene, ScenePath);
        AssetDatabase.SaveAssets();
        Debug.Log("Digicore final look applied to " + ScenePath);
    }

    private static void CreateSkyCeiling(Material magenta, Material cyan)
    {
        var root = new GameObject("Glitched Sky Ceiling");
        for (int i = 0; i < 55; i++)
        {
            var tile = GameObject.CreatePrimitive(PrimitiveType.Cube);
            tile.name = "Sky Fragment";
            tile.transform.SetParent(root.transform);
            tile.transform.position = new Vector3(Random.Range(-28f, 28f), Random.Range(12f, 20f), Random.Range(-8f, 42f));
            tile.transform.localScale = new Vector3(Random.Range(1f, 7f), Random.Range(.08f, .35f), Random.Range(.4f, 4f));
            tile.transform.rotation = Quaternion.Euler(Random.Range(-7f, 7f), Random.Range(0f, 360f), Random.Range(-5f, 5f));
            tile.GetComponent<Renderer>().sharedMaterial = i % 3 == 0 ? cyan : magenta;
            tile.AddComponent<GlitchPulse>();
        }
    }

    private static void CreateSparkField(Material white, Material magenta, Material cyan)
    {
        var root = new GameObject("Spark Field");
        for (int i = 0; i < 140; i++)
        {
            var spark = GameObject.CreatePrimitive(i % 3 == 0 ? PrimitiveType.Cube : PrimitiveType.Sphere);
            spark.name = "Digital Spark";
            spark.transform.SetParent(root.transform);
            spark.transform.position = new Vector3(Random.Range(-24f, 24f), Random.Range(.8f, 11f), Random.Range(-2f, 35f));
            float s = Random.Range(.04f, .18f);
            spark.transform.localScale = new Vector3(s, i % 3 == 0 ? s * 5f : s, s);
            spark.GetComponent<Renderer>().sharedMaterial = i % 5 == 0 ? cyan : (i % 2 == 0 ? white : magenta);
            Object.DestroyImmediate(spark.GetComponent<Collider>());
            spark.AddComponent<GlitchPulse>();
        }
    }

    private static void CreateDistantTower(Material magenta, Material cyan)
    {
        var root = new GameObject("Broken Data Tower");
        root.transform.position = new Vector3(0f, 0f, 24f);
        for (int i = 0; i < 38; i++)
        {
            var chunk = GameObject.CreatePrimitive(PrimitiveType.Cube);
            chunk.name = "Tower Chunk";
            chunk.transform.SetParent(root.transform);
            chunk.transform.localPosition = new Vector3(Random.Range(-2.4f, 2.4f), i * .7f + Random.Range(-.2f, .2f), Random.Range(-1.4f, 1.4f));
            chunk.transform.localScale = new Vector3(Random.Range(.5f, 3.5f), Random.Range(.25f, .8f), Random.Range(.5f, 2.5f));
            chunk.transform.rotation = Quaternion.Euler(Random.Range(-12f, 12f), Random.Range(-20f, 20f), Random.Range(-8f, 8f));
            chunk.GetComponent<Renderer>().sharedMaterial = i % 4 == 0 ? cyan : magenta;
            chunk.AddComponent<GlitchPulse>();
        }
    }

    private static void UpgradeCamera()
    {
        Camera cam = Camera.main;
        if (cam == null) return;
        cam.fieldOfView = 48f;
        cam.transform.position = new Vector3(0f, 3.4f, -13.5f);
        cam.transform.LookAt(new Vector3(0f, 2.6f, 9f));
        cam.allowHDR = true;
    }

    private static void UpgradeVolume()
    {
        Volume volume = Object.FindFirstObjectByType<Volume>();
        if (volume == null || volume.profile == null) return;

        if (volume.profile.TryGet(out Bloom bloom))
        {
            bloom.intensity.Override(2.6f);
            bloom.threshold.Override(.45f);
            bloom.scatter.Override(.85f);
        }
        if (volume.profile.TryGet(out ChromaticAberration chroma)) chroma.intensity.Override(.5f);
        if (volume.profile.TryGet(out Vignette vignette)) vignette.intensity.Override(.38f);
        if (volume.profile.TryGet(out ColorAdjustments color))
        {
            color.saturation.Override(48f);
            color.contrast.Override(28f);
            color.postExposure.Override(.35f);
        }
        if (!volume.profile.TryGet(out FilmGrain grain))
            grain = volume.profile.Add<FilmGrain>();
        grain.intensity.Override(.28f);
        grain.response.Override(.65f);
    }

    private static Material CreateGlitchMaterial(string name, Color baseColor, Color emission, Shader shader)
    {
        string path = "Assets/Materials/" + name + ".mat";
        Material material = AssetDatabase.LoadAssetAtPath<Material>(path);
        if (material == null)
        {
            material = new Material(shader != null ? shader : Shader.Find("Universal Render Pipeline/Unlit"));
            AssetDatabase.CreateAsset(material, path);
        }
        material.SetColor("_BaseColor", baseColor);
        material.SetColor("_EmissionColor", emission);
        material.SetFloat("_ScanlineDensity", 180f);
        material.SetFloat("_ScanlineStrength", .18f);
        return material;
    }
}
#endif
