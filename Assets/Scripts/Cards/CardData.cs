using UnityEngine;

[CreateAssetMenu(fileName = "NewCard", menuName = "MiniRoyale/Card")]
public class CardData : ScriptableObject
{
    public string cardName = "Knight";
    public int elixirCost = 3;
    public GameObject unitPrefab;
}
