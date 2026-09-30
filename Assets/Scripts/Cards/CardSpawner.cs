using UnityEngine;

public class CardSpawner : MonoBehaviour
{
    [SerializeField] private Camera mainCamera;
    [SerializeField] private ElixirSystem elixirSystem;
    [SerializeField] private CardData selectedCard;
    [SerializeField] private Team playerTeam = Team.Blue;
    [SerializeField] private float playerSideMaxY = 0f;

    private void Awake()
    {
        if (mainCamera == null)
            mainCamera = Camera.main;
    }

    private void Update()
    {
        if (GameManager.Instance != null && GameManager.Instance.MatchEnded)
            return;

        if (selectedCard == null || selectedCard.unitPrefab == null)
            return;

        if (Input.GetMouseButtonDown(0))
        {
            Vector3 world = mainCamera.ScreenToWorldPoint(Input.mousePosition);
            world.z = 0f;

            if (!IsValidPlacement(world))
                return;

            Spawn(world);
        }
    }

    public void SelectCard(CardData card)
    {
        selectedCard = card;
    }

    private bool IsValidPlacement(Vector3 worldPosition)
    {
        // Convenção deste protótipo:
        // jogador azul posiciona tropas na metade inferior (y <= 0)
        if (playerTeam == Team.Blue)
            return worldPosition.y <= playerSideMaxY;

        return worldPosition.y >= -playerSideMaxY;
    }

    private void Spawn(Vector3 position)
    {
        if (!elixirSystem.TrySpend(selectedCard.elixirCost))
        {
            Debug.Log("Elixir insuficiente.");
            return;
        }

        GameObject unit = Instantiate(selectedCard.unitPrefab, position, Quaternion.identity);

        Unit unitData = unit.GetComponent<Unit>();
        if (unitData != null)
            unitData.SetTeam(playerTeam);
    }
}
