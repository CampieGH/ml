using UnityEngine;

public sealed class OrbitCamera : MonoBehaviour
{
    [SerializeField] private Transform target;
    [SerializeField] private float distance = 22f;
    [SerializeField] private float height = 10f;
    [SerializeField] private float speed = 8f;

    private void LateUpdate()
    {
        if (target == null)
        {
            return;
        }

        float angle = Time.time * speed;
        Vector3 offset = Quaternion.Euler(0f, angle, 0f) * new Vector3(0f, height, -distance);
        transform.position = target.position + offset;
        transform.LookAt(target.position + Vector3.up * 2f);
    }

    public void SetTarget(Transform newTarget)
    {
        target = newTarget;
    }
}
