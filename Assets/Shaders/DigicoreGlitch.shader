Shader "ML/DigicoreGlitch"
{
    Properties
    {
        _BaseColor ("Base Color", Color) = (1,0,1,1)
        _EmissionColor ("Emission", Color) = (1,0,1,1)
        _Glitch ("Glitch", Range(0,1)) = 0
        _ScanlineDensity ("Scanline Density", Float) = 180
        _ScanlineStrength ("Scanline Strength", Range(0,1)) = 0.2
    }

    SubShader
    {
        Tags { "RenderType"="Opaque" "RenderPipeline"="UniversalPipeline" }

        Pass
        {
            Name "ForwardUnlit"
            Tags { "LightMode"="UniversalForward" }

            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            struct Attributes
            {
                float4 positionOS : POSITION;
                float2 uv : TEXCOORD0;
            };

            struct Varyings
            {
                float4 positionHCS : SV_POSITION;
                float2 uv : TEXCOORD0;
                float3 positionWS : TEXCOORD1;
            };

            CBUFFER_START(UnityPerMaterial)
                float4 _BaseColor;
                float4 _EmissionColor;
                float _Glitch;
                float _ScanlineDensity;
                float _ScanlineStrength;
            CBUFFER_END

            Varyings vert(Attributes input)
            {
                Varyings output;
                float3 positionOS = input.positionOS.xyz;
                float slice = floor(positionOS.y * 8.0 + _Time.y * 9.0);
                float randomShift = frac(sin(slice * 17.13) * 43758.5453) - 0.5;
                positionOS.x += randomShift * _Glitch * 0.22;
                VertexPositionInputs pos = GetVertexPositionInputs(positionOS);
                output.positionHCS = pos.positionCS;
                output.positionWS = pos.positionWS;
                output.uv = input.uv;
                return output;
            }

            half4 frag(Varyings input) : SV_Target
            {
                float scan = sin(input.positionHCS.y * _ScanlineDensity * 0.01 + _Time.y * 18.0);
                scan = lerp(1.0, 0.5 + 0.5 * scan, _ScanlineStrength);

                float noise = frac(sin(dot(floor(input.positionHCS.xy * 0.25), float2(12.9898, 78.233)) + floor(_Time.y * 12.0)) * 43758.5453);
                float glitchFlash = step(0.97, noise) * _Glitch;

                float3 color = _BaseColor.rgb * scan + _EmissionColor.rgb;
                color += glitchFlash * float3(0.25, 0.9, 1.3);
                return half4(color, _BaseColor.a);
            }
            ENDHLSL
        }
    }
}
