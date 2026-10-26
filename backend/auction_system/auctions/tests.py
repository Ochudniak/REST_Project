from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Auction, Bid


# Testy API dla obsługi aukcji
class AuctionApiTest(APITestCase):
    # Przygotowanie przykładowej aukcji
    def setUp(self):
        self.auction = Auction.objects.create(
            name="testname",
            description="testdescription",
            category="testcategory",
            starting_price="100.00",
            current_price="100.00",
            start_date=timezone.now() - timedelta(days=3),
            end_date=timezone.now() + timedelta(days=1),
            owner_id=1,
            status="active",
        )

    # Test tworzenia nowej aukcji
    def test_create_auction(self):
        data = {
            "name": "newauction",
            "description": "newdescription",
            "category": "newcategory",
            "starting_price": "200.00",
            "start_date": (timezone.now() - timedelta(days=3)).isoformat(),
            "end_date": (timezone.now() + timedelta(days=2)).isoformat(),
            "owner_id": 1,
            "status": "active",
        }

        response = self.client.post("/api/auctions/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(Auction.objects.filter(name="newauction").exists())

    def test_create_future_auction(self):
        auction = Auction.objects.create(
            name = "newauction",
            description =  "newdescription",
            category = "newcategory",
            starting_price = "200.00",
            current_price = "200.00",
            start_date = timezone.now() + timedelta(days=3),
            end_date = timezone.now() + timedelta(days=5),
            owner_id = 1,
            status = "active"
        )

        auction.update_status()
        auction.refresh_from_db()
        
        self.assertEqual(auction.status, "planned")
        
        self.assertTrue(Auction.objects.filter(name="newauction").exists())

    def test_ended_auction(self):
        auction = Auction.objects.create(
            name = "newauction",
            description =  "newdescription",
            category = "newcategory",
            starting_price = "200.00",
            current_price = "200.00",
            start_date = timezone.now() - timedelta(days=5),
            end_date = timezone.now() - timedelta(days=2),
            owner_id = 1,
            status = "active"
        )
        
        auction.update_status()
        auction.refresh_from_db()
                
        self.assertEqual(auction.status, "ended")
                
        self.assertTrue(Auction.objects.filter(name="newauction").exists())
        
    

    # Test pobierania listy aukcji
    def test_get_auction_list(self):
        response = self.client.get("/api/auctions/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    # Test pobierania jednej aukcji
    def test_get_single_auction(self):
        response = self.client.get(f"/api/auctions/{self.auction.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Test pobierania aukcji po id
    def test_get_auction_by_id(self):
        response = self.client.get(f"/api/auctions/{self.auction.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data["name"], "testname")

    # Test edycji aukcji
    def test_update_auction(self):
        data = {
            "name": "newauction",
            "description": "newdescription",
            "category": "newcategory",
            "starting_price": "150.00",
            "start_date": (timezone.now() - timedelta(days=1)).isoformat(),
            "end_date": (timezone.now() + timedelta(days=3)).isoformat(),
            "owner_id": 1,
            "status": "active",
        }

        response = self.client.put(
            f"/api/auctions/{self.auction.id}/", data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.auction.refresh_from_db()

        self.assertEqual(self.auction.name, "newauction")
        self.assertEqual(self.auction.description, "newdescription")
        self.assertEqual(self.auction.category, "newcategory")

    # Test usuwania aukcji
    def test_delete_auction(self):
        response = self.client.delete(f"/api/auctions/{self.auction.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        exists = Auction.objects.filter(id=self.auction.id).exists()

        self.assertEqual(exists, False)

    # Test filtrowania aukcji po statusie
    def test_filter_auctions_by_status(self):
        Auction.objects.create(
            name="Telefon",
            description="Opis",
            category="elektronika",
            starting_price="800.00",
            current_price="800.00",
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=1),
            owner_id=2,
            status="ended",
        )

        response = self.client.get("/api/auctions/?status=active")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)


class BiddingTests(APITestCase):
    def setUp(self):
        self.auction = Auction.objects.create(
            name="testname",
            description="testdescription",
            category="testcategory",
            starting_price="100.00",
            current_price="100.00",
            start_date=timezone.now() - timedelta(days=3),
            end_date=timezone.now() + timedelta(days=1),
            owner_id=1,
            status="active",
        )

    def test_create_bid(self):
        data = {"amount": "150.00"}

        response = self.client.post(
            f"/api/auctions/{self.auction.id}/bids/", data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(
            Bid.objects.filter(auction=self.auction, amount="150.00").exists()
        )

    def test_wrong_amount_format(self):
        data = {"amount": "abcd"}

        response = self.client.post(
            f"/api/auctions/{self.auction.id}/bids/", data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_bid_must_be_higher_than_current_price(self):
        data = {"amount": "90.00"}

        response = self.client.post(
            f"/api/auctions/{self.auction.id}/bids/", data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_bid_updates_current_price(self):
        data = {"amount": "180.00"}

        response = self.client.post(
            f"/api/auctions/{self.auction.id}/bids/", data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.auction.refresh_from_db()

        self.assertEqual(str(self.auction.current_price), "180.00")

    def test_cannot_bid_on_ended_auction(self):
        self.auction.end_date = timezone.now() - timedelta(hours=3)
        self.auction.save()

        data = {"amount": "150.00"}

        response = self.client.post(
            f"/api/auctions/{self.auction.id}/bids/", data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
