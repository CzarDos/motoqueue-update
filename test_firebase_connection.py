"""
Firebase Connection Test Script
================================
This script tests your Firebase connection and shows sample data
from your Firestore database to verify everything is set up correctly.
"""

import sys
import os

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

def test_firebase_connection():
    """Test Firebase connection and display sample data."""
    
    print("="*70)
    print("FIREBASE CONNECTION TEST")
    print("="*70)
    
    try:
        # Initialize Firebase
        print("\n1. Testing Firebase initialization...")
        cred = credentials.Certificate('firebase_credentials.json')
        firebase_admin.initialize_app(cred)
        print("   ✓ Firebase initialized successfully")
        
        # Get Firestore client
        db = firestore.client()
        print("   ✓ Firestore client created")
        
        # Test spare_parts collection
        print("\n2. Testing spare_parts collection...")
        parts_ref = db.collection('spare_parts')
        parts_docs = list(parts_ref.limit(5).stream())
        
        if parts_docs:
            print(f"   ✓ Found {len(parts_docs)} spare parts (showing first 5)")
            for doc in parts_docs:
                part = doc.to_dict()
                print(f"      - {part.get('name', 'Unknown')} (SKU: {part.get('sku', 'N/A')})")
        else:
            print("   ⚠ No spare parts found in collection")
        
        # Test appointments collection
        print("\n3. Testing appointments collection...")
        appointments_ref = db.collection('appointments')
        appointments_docs = list(appointments_ref.limit(5).stream())
        
        if appointments_docs:
            print(f"   ✓ Found {len(appointments_docs)} appointments (showing first 5)")
            
            completed_count = 0
            appointments_with_parts = 0
            
            for doc in appointments_docs:
                appointment = doc.to_dict()
                status = appointment.get('status', 'unknown')
                spare_parts = appointment.get('spareParts', [])
                
                print(f"      - {doc.id}")
                print(f"        Status: {status}")
                print(f"        Spare parts: {len(spare_parts)}")
                
                if 'complete' in status.lower():
                    completed_count += 1
                
                if spare_parts:
                    appointments_with_parts += 1
                    # Show first part as example
                    if isinstance(spare_parts, list) and len(spare_parts) > 0:
                        first_part = spare_parts[0]
                        if isinstance(first_part, dict):
                            print(f"        Example part: {first_part.get('name')} (qty: {first_part.get('quantity')})")
            
            print(f"\n   Statistics from sample:")
            print(f"      Completed appointments: {completed_count}/{len(appointments_docs)}")
            print(f"      Appointments with parts: {appointments_with_parts}/{len(appointments_docs)}")
        else:
            print("   ⚠ No appointments found in collection")
        
        # Count total completed appointments with spare parts
        print("\n4. Counting usable historical data...")
        all_appointments = db.collection('appointments').stream()
        
        total_count = 0
        completed_with_parts = 0
        total_parts_used = 0
        
        for doc in all_appointments:
            total_count += 1
            appointment = doc.to_dict()
            status = appointment.get('status', '').lower()
            spare_parts = appointment.get('spareParts', [])
            
            if 'complete' in status and spare_parts:
                completed_with_parts += 1
                if isinstance(spare_parts, list):
                    total_parts_used += sum(
                        part.get('quantity', 0) 
                        for part in spare_parts 
                        if isinstance(part, dict)
                    )
        
        print(f"   ✓ Total appointments: {total_count}")
        print(f"   ✓ Completed with spare parts: {completed_with_parts}")
        print(f"   ✓ Total parts used: {total_parts_used}")
        
        # Recommendations
        print("\n" + "="*70)
        print("ASSESSMENT")
        print("="*70)
        
        if completed_with_parts >= 30:
            print("✓ EXCELLENT: You have enough historical data to train a good model")
            print(f"  {completed_with_parts} completed appointments with spare parts usage")
        elif completed_with_parts >= 10:
            print("⚠ MODERATE: You have some historical data, model will improve over time")
            print(f"  {completed_with_parts} completed appointments with spare parts usage")
            print("  Recommendation: Continue collecting data and retrain weekly")
        else:
            print("⚠ LIMITED: You have minimal historical data")
            print(f"  {completed_with_parts} completed appointments with spare parts usage")
            print("  Recommendation: Collect at least 30 completed appointments before training")
            print("  The model will work but predictions may be less accurate initially")
        
        print("\n" + "="*70)
        print("✓ CONNECTION TEST SUCCESSFUL")
        print("="*70)
        print("\nNext step: Run 'python train_model.py' to train the forecasting model")
        print("="*70)
        
    except FileNotFoundError:
        print("\n✗ ERROR: firebase_credentials.json not found")
        print("\nPlease follow these steps:")
        print("1. Go to Firebase Console → Project Settings → Service Accounts")
        print("2. Click 'Generate New Private Key'")
        print("3. Save the file as 'firebase_credentials.json' in this directory")
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        print("\nTroubleshooting:")
        print("- Verify firebase_credentials.json contains valid credentials")
        print("- Check that your service account has Firestore read permissions")
        print("- Ensure you selected the correct Firebase project")

if __name__ == "__main__":
    test_firebase_connection()

