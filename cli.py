import click
import requests

BASE_URL = "http://localhost:8000"

@click.group()
def cli():
    pass

@cli.command()
@click.argument('address')
def search(address):
    """Cerca parcheggi per indirizzo"""
    response = requests.post(f"{BASE_URL}/find-parking", json={"address": address})
    
    if response.status_code != 200:
        click.echo(f"Errore: {response.text}")
        return
    
    data = response.json()
    
    click.echo(f"\n📍 Posizione utente: {data['user_location']}")
    click.echo("\n🏆 Migliori parcheggi:")
    for i, park in enumerate(data['top_parkings']):
        color = {
            'green': '🟢',
            'yellow': '🟡',
            'red': '🔴'
        }.get(park['color'], '⚪')
        
        click.echo(
            f"{i+1}. {color} {park['address']} "
            f"\n   Distanza: {park['distance']:.2f} km - "
            f"Disponibilità: {park['availability_prob']:.0%}"
        )
    
    click.echo("\n📋 Tutti i parcheggi:")
    for i, park in enumerate(data['all_parkings']):
        status = '🟢' if park['availability_prob'] > 0.7 else '🟡' if park['availability_prob'] > 0.4 else '🔴'
        click.echo(f"{i+1}. {status} {park['address']}")

@cli.command()
@click.option('--lat', type=float, required=True, help='Latitudine')
@click.option('--lng', type=float, required=True, help='Longitudine')
@click.option('--address', required=True, help='Indirizzo completo')
@click.option('--covered', type=bool, help='Coperto (true/false)')
@click.option('--paid', type=bool, help='A pagamento (true/false)')
@click.option('--capacity', type=int, help='Capienza approssimativa')
def register(lat, lng, address, covered, paid, capacity):
    """Registra un nuovo parcheggio"""
    data = {
        "latitude": lat,
        "longitude": lng,
        "address": address,
        "covered": covered,
        "paid": paid,
        "capacity": capacity
    }
    
    response = requests.post(f"{BASE_URL}/register-parking", json=data)
    
    if response.status_code == 200:
        result = response.json()
        click.echo(f"✅ Parcheggio registrato con ID: {result['id']}")
    else:
        click.echo(f"❌ Errore: {response.text}")

@cli.command()
@click.option('--parking-id', required=True, help='ID parcheggio')
@click.option('--free-spots', type=int, required=True, help='Posti liberi vicini')
@click.option('--parked', type=bool, required=True, help='Parcheggiato con successo (true/false)')
def feedback(parking_id, free_spots, parked):
    """Invia feedback per un parcheggio"""
    data = {
        "parking_id": parking_id,
        "free_spots": free_spots,
        "parked_success": parked
    }
    
    response = requests.post(f"{BASE_URL}/submit-feedback", json=data)
    
    if response.status_code == 200:
        click.echo("✅ Feedback inviato con successo!")
    else:
        click.echo(f"❌ Errore: {response.text}")

if __name__ == '__main__':
    cli()