using System;
using System.Collections.Generic;
using System.Drawing;
using System.Net.Http;
using System.Net.Http.Json;
using System.Windows.Forms;
using System.Threading.Tasks;

namespace ClienteCaixa;

// 1. MODELO
public class Medicine {
    public int id { get; set; }
    public string name { get; set; }
    public float price { get; set; }
    public int quantity { get; set; }
    public string category { get; set; }
}

// 2. A TELA (FORM)
public class PharmacyForm : Form { // Note que a classe se chama PharmacyForm
    private const string API_URL = "http://localhost:8000";
    private readonly HttpClient client = new HttpClient();
    
    private DataGridView grid;
    private Button btnSell;
    private Button btnRefresh;
    private Label lblStatus;

    // O Construtor tem o MESMO nome da classe
    public PharmacyForm() {
        this.Text = "PDV - Caixa Farmácia";
        this.Size = new Size(650, 500);
        this.StartPosition = FormStartPosition.CenterScreen;
        
        SetupUI();
        _ = LoadData();
    }

    private void SetupUI() {
        grid = new DataGridView { 
            Location = new Point(10, 10), 
            Size = new Size(610, 350),
            AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.Fill,
            SelectionMode = DataGridViewSelectionMode.FullRowSelect,
            MultiSelect = false,
            ReadOnly = true,
            AllowUserToAddRows = false
        };

        btnSell = new Button { 
            Text = "VENDER (-1 unid)", 
            Location = new Point(10, 370), 
            Size = new Size(150, 40),
            BackColor = Color.LightGreen,
            Font = new Font("Arial", 10, FontStyle.Bold)
        };
        btnSell.Click += async (s, e) => await SellSelectedItem();

        btnRefresh = new Button { 
            Text = "Atualizar Lista", 
            Location = new Point(170, 370), 
            Size = new Size(120, 40) 
        };
        btnRefresh.Click += async (s, e) => await LoadData();

        lblStatus = new Label { 
            Text = "Conectando...", 
            Location = new Point(10, 420), 
            AutoSize = true,
            ForeColor = Color.Blue
        };

        this.Controls.Add(grid);
        this.Controls.Add(btnSell);
        this.Controls.Add(btnRefresh);
        this.Controls.Add(lblStatus);
    }

    private async Task LoadData() {
        try {
            var meds = await client.GetFromJsonAsync<List<Medicine>>($"{API_URL}/medicines");
            grid.DataSource = meds;
            lblStatus.Text = $"Atualizado às: {DateTime.Now.ToLongTimeString()}";
            lblStatus.ForeColor = Color.Green;
        } catch {
            lblStatus.Text = "ERRO: Servidor Python desligado?";
            lblStatus.ForeColor = Color.Red;
        }
    }

    private async Task SellSelectedItem() {
        if (grid.SelectedRows.Count == 0) return;
        var med = (Medicine)grid.SelectedRows[0].DataBoundItem;
        try {
            var response = await client.PostAsync($"{API_URL}/sell/{med.id}/1", null);
            if (response.IsSuccessStatusCode) {
                await LoadData();
                MessageBox.Show($"Venda de {med.name} realizada!");
            }
        } catch {
            MessageBox.Show("Erro de conexão.");
        }
    }
}

// 3. O INÍCIO DO PROGRAMA
static class Program {
    [STAThread]
    static void Main() {
        Application.SetHighDpiMode(HighDpiMode.SystemAware);
        Application.EnableVisualStyles();
        Application.SetCompatibleTextRenderingDefault(false);
        // Manda rodar o PharmacyForm definido acima
        Application.Run(new PharmacyForm());
    }
}